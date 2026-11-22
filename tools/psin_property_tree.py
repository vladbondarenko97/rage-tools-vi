"""Parse the PSIN typed property array and test 64-bit name-hash variants.

The large PSIN blocks are flat arrays of 16-byte records

    u32 value; u32 type; u32 class_hash; u32 field_hash;   type in {0x101..0x105}

The value is a union: float when type is 0x102, a byte-sized int for 0x101 and
0x105, a 32-bit hash for 0x103, bool for 0x104. There are 303 distinct class
hashes and 14,655 distinct field hashes; the (class, field) pair fixes the type
for 97.3 % of pairs. Records are recovered by
scanning every record-aligned position in the PSIN section and keeping maximal
runs of at least four records whose type word is valid; that is robust to the
2-byte misalignment seen at the end of the block directory.

Modes:

    # inventory: how many records, types, distinct name hashes
    python3 tools/psin_property_tree.py

    # dump every record
    python3 tools/psin_property_tree.py --dump cache/psin-properties.tsv

    # try 64-bit hash variants of known names against the name-hash column
    python3 tools/psin_property_tree.py --hash-test
"""

import argparse
import csv
import struct
import zlib
from collections import Counter, defaultdict
from pathlib import Path

TYPES = {0x101, 0x102, 0x103, 0x104, 0x105}
TYPE_NAMES = {0x101: "int", 0x102: "float", 0x103: "type103",
              0x104: "type104", 0x105: "type105"}


def sections(body):
    out = []
    offset = 0
    while offset + 8 <= len(body):
        tag = body[offset:offset + 4].decode("ascii", "ignore")
        size = struct.unpack_from(">I", body, offset + 4)[0]
        if not tag.isupper() or size < 8 or offset + size > len(body):
            break
        out.append((tag, offset, size))
        offset += size
    return out


def psin_sections(archive, index):
    rows = sorted((int(r["start"], 16), int(r["end"], 16))
                  for r in csv.DictReader(index.open(), delimiter="\t")
                  if r["kind"] == "zlib")
    data = archive.read_bytes()
    out = []
    position = 0
    while position < len(rows):
        start, end = rows[position]
        try:
            body = zlib.decompress(data[start:end])
        except zlib.error:
            position += 1
            continue
        if body.startswith(b"PSIN"):
            if len(body) == 65536 and position + 1 < len(rows):
                nxt_start, nxt_end = rows[position + 1]
                try:
                    body += zlib.decompress(data[nxt_start:nxt_end])
                except zlib.error:
                    pass
            for tag, offset, size in sections(body):
                if tag == "PSIN":
                    out.append((position, body[offset + 8:offset + size]))
        position += 1
    return out


def runs(psin):
    """Maximal runs of >=4 valid 16-byte records."""
    found = []
    current = None
    for offset in range(0, (len(psin) // 16) * 16, 16):
        value, kind, name = struct.unpack_from("<IIQ", psin, offset)
        if kind in TYPES:
            if current is None:
                current = []
            current.append((offset, value, kind, name))
        else:
            if current and len(current) >= 4:
                found.append(current)
            current = None
    if current and len(current) >= 4:
        found.append(current)
    return found


def collect(archive, index):
    records = []
    for position, psin in psin_sections(archive, index):
        for run in runs(psin):
            for offset, value, kind, name in run:
                records.append((position, offset, value, kind, name))
    return records


# ---- 64-bit hash variants ------------------------------------------------

MASK64 = (1 << 64) - 1


def joaat64(text):
    value = 0
    for byte in text:
        value = (value + byte) & MASK64
        value = (value + (value << 10)) & MASK64
        value ^= value >> 6
    value = (value + (value << 3)) & MASK64
    value ^= value >> 11
    value = (value + (value << 15)) & MASK64
    return value


def fnv1a64(text):
    value = 0xcbf29ce484222325
    for byte in text:
        value ^= byte
        value = (value * 0x100000001b3) & MASK64
    return value


def murmur64a(text, seed=0):
    m = 0xc6a4a7935bd1e995
    r = 47
    length = len(text)
    value = (seed ^ (length * m)) & MASK64
    position = 0
    while length - position >= 8:
        (block,) = struct.unpack_from("<Q", text, position)
        block = (block * m) & MASK64
        block ^= block >> r
        block = (block * m) & MASK64
        value ^= block
        value = (value * m) & MASK64
        position += 8
    tail = text[position:]
    for index, byte in enumerate(reversed(tail)):
        value ^= byte << (index * 8)
    if tail:
        value = (value * m) & MASK64
    value ^= value >> r
    value = (value * m) & MASK64
    value ^= value >> r
    return value


VARIANTS = {"joaat64": joaat64, "fnv1a64": fnv1a64,
            "murmur64a": murmur64a,
            "murmur64a_seed1": lambda t: murmur64a(t, 1)}


def name_corpus():
    names = set()
    for path in list(Path("handoff").glob("*.tsv")):
        try:
            rows = list(csv.DictReader(path.open(), delimiter="\t"))
        except Exception:
            continue
        for row in rows:
            for column, value in row.items():
                if not value or not column:
                    continue
                lowered = column.lower()
                if ("name" in lowered or "path" in lowered or "root" in lowered) \
                        and len(value) < 96 and " " not in value.strip():
                    names.add(value.strip())
    return names


def hash_test(records):
    corpus = sorted(name_corpus())
    print(f"names in corpus: {len(corpus)}")
    wanted = {name for _, _, _, _, name in records}
    print(f"distinct name hashes to explain: {len(wanted)}")
    best = Counter()
    for variant, function in VARIANTS.items():
        hits = 0
        examples = []
        for name in corpus:
            for form in (name, name.lower(), name.upper(),
                         name.lower().rsplit(".", 1)[0]):
                encoded = form.encode()
                if function(encoded) in wanted:
                    hits += 1
                    if len(examples) < 3:
                        examples.append((form, hex(function(encoded))))
        best[variant] = hits
        print(f"  {variant:16s} hits {hits:>5}  examples {examples}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path("script.rpf"))
    parser.add_argument("--index", type=Path, default=Path("output/index/script.tsv"))
    parser.add_argument("--dump", type=Path, help="write records as TSV")
    parser.add_argument("--hash-test", action="store_true")
    args = parser.parse_args()

    records = collect(args.archive, args.index)
    print(f"records: {len(records):,} across "
          f"{len({r[0] for r in records})} PSIN sections")
    kinds = Counter(record[3] for record in records)
    print("types:", {TYPE_NAMES[k]: n for k, n in kinds.most_common()})
    classes = Counter(record[4] & 0xffffffff for record in records)
    fields = Counter(record[4] >> 32 for record in records)
    print(f"distinct class hashes: {len(classes):,}; distinct field hashes: "
          f"{len(fields):,}")
    print(f"fields per class: max {max(classes.values()):,}; "
          f"top class {classes.most_common(1)[0][1]:,} records")
    per = Counter(record[0] for record in records)
    counts = sorted(per.values())
    print(f"per PSIN section: min {counts[0]}, median {counts[len(counts)//2]}, "
          f"max {counts[-1]}")

    if args.dump:
        args.dump.parent.mkdir(parents=True, exist_ok=True)
        with args.dump.open("w") as handle:
            handle.write("psin\toffset\tvalue\ttype\tclass_hash\tfield_hash\tas_float\n")
            for section, offset, value, kind, name in records:
                as_float = struct.unpack("<f", struct.pack("<I", value))[0]
                handle.write(f"{section}\t0x{offset:x}\t0x{value:08x}\t"
                             f"0x{kind:03x}\t0x{name & 0xffffffff:08x}\t"
                             f"0x{name >> 32:08x}\t{as_float:g}\n")
        print(f"wrote {args.dump}")

    if args.hash_test:
        hash_test(records)


if __name__ == "__main__":
    main()
