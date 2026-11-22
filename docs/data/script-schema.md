# Script schema (PSIN)

`script.rpf` records are not bytecode. Each one carries a section sequence —
`PSIN`, `LSCH`, `LENM`, `LSNS`, `LGID`, `LRSC`, `CHKS` — and `PSIN` holds a flat
array of 16-byte rows:

```
struct PsinRow {          // 62,910 rows across 1,012 records
    u32 value;            // union: float when type == 0x102
    u32 type;             // 0x101 int, 0x102 float, 0x103 hash, 0x104 bool, 0x105 byte
    u32 property;         // 301 distinct — names like Position, Flags, Heading
    u32 key;              // 14,653 distinct — names like CAR, bonnet, ambrosia
};
```

Rows are recovered by scanning every record-aligned position and keeping maximal
runs whose type word is in range, because the block directory does not align with
record boundaries at the end of a block.

## Reading it

```bash
python3 tools/psin_extract.py script.rpf          # 62,910 rows -> cache/
python3 tools/psin_dump.py --record 110           # the rows, with names
python3 tools/psin_segment.py --describe 1054     # as paired entries
python3 tools/psin_entries.py                     # every pair, 4,968 of them
```

Record 1054 is the vehicle customisation table:

```
  2  Type=Default      Id=0x00000000
  3  Type=location     Id=CAR
  4  Type=0x00000003   Id=motorbike
  6  Type=0x00000006   Id=cosmetics
  8  Type=0x00000009   Id=bonnet
 10  Type=0x0000000b   Id=side
 13  Type=0x0000000e   Id=roof
```

Two details make that readable and both were learned the hard way: on `Id`/`Type`
rows the payload is the **key** (the value column holds an ordinal), and the
pairing is **local** — only one record in 868 repeats with period 2 throughout, so
the renderer pairs run by run rather than assuming a layout.

## What is named, and what is not

| Namespace | Size | Resolved | How |
| --- | ---: | ---: | --- |
| properties | 301 | 25 | corpus + engine metadata |
| keys | 14,653 | 515 | corpus |
| types (`root_type`, `type_tag`) | 42 | 0 | not a vocabulary problem — see below |

The type namespace is 21 `root_type` and 21 `type_tag` values. Three vocabularies
return nothing against it: the 174k corpus (0 hits, 1.42 expected by chance),
20,300 engine metadata names (4 doubtful hits in 234,720 values), and 40 engine
class names (0 hits). A namespace that small would fall to any decent word list if
its names were plain strings, so the names are most likely stored as text inside
`LSNS`.

## What LSNS is

`LSNS` is a **table container**, not a cipher. Its payload is

```
u32 table count N | 4 flag bytes | per table: u32 length (then u32 id, except last)
```

with every length a multiple of 16 and `header + sum(lengths)` equal to the payload
size. That framing holds on **1,012 of 1,012** records, giving 58,697 sixteen-byte
records (`tools/lsns_tables.py`).

An earlier reading of this section as an encrypted blob was wrong, and the
measurements behind it were right about the bytes and wrong about their meaning:
the "120 identical 160-byte bodies" are the 120 tables of exactly ten records, the
16-byte blocking is the record size, and the uniform entropy is what four
hash-like words per record look like.

Each table is `[path of ≤10 × 128-bit levels][per-script tail]`:

- the path is a **trie**. Require more leading records and the group shrinks — 853
  tables share level 1, 381 share all ten, and 120 scripts share the full path.
  So the head encodes a hierarchy of script kinds, visible but unlabelled.
- the tail is per-script data. Within one kind every tail differs, but its length
  is fixed (22–23, 19–20, 20–21 in three sampled groups), off by one for a
  minority — what an optional trailing record looks like.
- 120 tables are path only, with no tail at all.

The records are not sorted in any interpretation (0 of 994 tables ascending as
u128, as two u64, or as four u32), so the order carries no index-like structure.
The values themselves remain opaque: 210,522 distinct words, none matching a known
name or a PSIN key, and no slot holding a small integer.

What remains masked in `script.rpf` is the 331,728-byte blob, which has entropy
7.996 and no zlib stream at its start.
