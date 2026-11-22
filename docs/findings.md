# What we found

A summary of the verified results, written for a reader who has not followed the
journal. Each claim links to the page or artifact that proves it; the append-only
evidence lives in `investigation.md`.

## The container

RPF9 is a 0x60-byte header followed by three metadata regions and a payload:

| Region | Bounds | State |
| --- | --- | --- |
| Header | `0x00..0x60` | mapped, 24 words |
| Front A | `0x60..+0x08` | **masked**; holds names and paths |
| Front B | `+0x08..+0x04` | **masked**; the entry table |
| Payload | Front B end .. trailer | zlib chains, opaque spans, zero runs |
| Trailer | `end - +0x0c .. end` | **masked**; CBC-like, pack-independent chain |

The header fields are known well enough to predict sizes without decoding:
`+0x0c` is the trailer length in all 4,373 headers censused, and Front B is
`align16(9N)` or `align16(10N)` exactly — selected by a count-driven tag — for
all 2,908 mode-family-1 headers. Every payload stream is located by scanning and
checksum verification, not by the table.

## Coverage

All 22 source archives are indexed: **4,415,850 ranges / 161.3 GB stored /
365.0 GB decoded**, and every index tiles its archive exactly, with no gap and no
overlap. Six archives plus `levels` carry bulk extraction manifests covering
2,190,635 zlib ranges; each extraction is SHA-256 verified.

The unclassified layer is **closed**: every large span is media. 38.1 GB of AWC
audio, 13.4 GB of Bink/Bink2 video, ~1.2 GB of fragments. There is no unexplained
game payload left in it.

## Entry identity from the payload

The index table is masked, so entries are identified from the payload instead:

| Archive | Unit | Packs verified | Entries |
| --- | --- | ---: | ---: |
| `core_bvh4` | pairs | **1,253 / 1,261** | 109,301 |
| `navmeshes` | chains | 14 / 28 | 23,530 |
| `packs` | pairs | 20 / 59 | 15,983 |
| `levels` | pairs | 728 / 2,044 | 29,117 |
| `anim` | chains | 125 / 235 | 5,826 |
| `data` | chains | 16 / 40 | 2,063 |
| `textures` | pairs | 17 / 20 | 1,326 |

**188,298 entries** with exact, payload-derived boundaries and an independent
check against the declared count, across **14 archives**; the table above shows the
largest. Every pack contributed only when its entry count verified exactly, and the
full per-archive table is [the corpus pass](extraction/corpus.md).

## Naming

Every identifier encountered is `JOAAT(lowercase name)`. That single fact turned
hash tables into readable rigs:

- **99 of 612** class-0 bone-table hashes and **21 of 252** weight hashes resolve
  through the `skel_` / `mh_` / `rb_` families (skeleton, muscle helpers, ragdoll).
- One rig is fully decoded: root `0x48dcbb01`, 34/34 bones — a two-sided
  hand/forearm rig with four three-segment finger chains.
- The 16 skeleton families carry readings: a hand rig, a genital rig, large
  animals, and a small-prop population that still holds an unnamed 330-hash
  universe.

## Audio

`audio.rpf`'s 23.5 GB of AWC containers decode completely: **93,344 Opus, 1,818
XMA2 and 73 ACE1** streams with zero failures. The check that makes it trustworthy
is `frames × channels / declared`, which is **1.002 at the 1st percentile** — the
declared count is interleaved across channels, so a naive `frames / declared` halves
every stereo stream.

`story000` turned out to hold a second, larger audio archive: 9.56 GB of AWC in a
different container variant, decoded to **196,350 Opus streams / 148.3 hours**.

The three container variants share one record format (`type:8 | size:28 | offset:28`)
but not one table position. `0xff02` computes it; `0xff21`/`0xff61` carry it as the
longest valid 8-byte-aligned suffix before the data offset, which a scan finds
every time (`tools/awc_chunk_table.py`).

## Script schema

`script.rpf` records are a section sequence, not bytecode. `PSIN` holds a flat
array of 16-byte rows `(value, type, property, key)`: **62,910 rows** across 1,012
records, of which 25 of 301 property names and 515 of 14,653 object keys are
recovered.

`PSIN` itself is a general envelope — **≈18,637 records across ten archives** — but
the property array is a single-file feature: scanning every body at every byte offset
finds rows only in `script.rpf` (plus 28 rows in two `packs.rpf` records). Three
layouts carry the envelope, and the other two hold different payloads.

The same container appears in `levels.rpf`, where **5,116** streams carry the
identical section sequence but a different payload (the unversioned layout, with
32-byte rows rather than the 16-byte property array).

`LSNS` is a table container, not a cipher: framing validates on **1,012 of 1,012**
records, 58,697 sixteen-byte records. Each table is `[path of ≤10 × 128-bit
levels][per-script tail]`, and the path is a trie — 853 tables share level 1, 381
share all ten — so it encodes a hierarchy of script kinds while its labels stay
opaque.

## What is not solved

- Front A, Front B and the trailer are masked. The size laws are known; the
  contents are not. Four metadata questions are blocked on key material or a
  crib, not on effort.
- The remaining 330-hash universe is a vocabulary problem: the names are not in
  the corpora harvested so far.
- `core_bvh4` reproduces the declared count for **1,253 of 1,261 packs**; the rest,
  and most of `levels`, have one to four entries per pack whose descriptor is not
  where the stream window says it should be.

See the [roadmap](roadmap.md) for the live list.
