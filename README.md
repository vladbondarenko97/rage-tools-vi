# Rage Tools VI

RPF9 archive extraction, entry reconstruction and identifier recovery for
**GTA VI / Leonida** — built as an evidence problem, not a guessing game.

> **Goal:** enumerate every archive entry, locate its stored bytes, decode it, and
> say what it is.

## The idea in three lines

RPF9 archives hide their table of contents behind masked metadata, so this project
reconstructs entries from the **payload** and uses the masked table only as a
cross-check:

- every payload range is found by scanning and **verified by zlib checksum**;
- every pack declares an entry count `N`, so the count is an **oracle**: an entry
  model that does not reproduce `N` exactly is rejected;
- every identifier met so far is **`JOAAT(lowercase name)`**, so names are
  recoverable by vocabulary instead of by key.

Full walkthrough: **[From first principles](docs/explained.md)**.

## Results

| Area | Result |
| --- | --- |
| Corpus index | **22 archives · 4,415,850 ranges · 161.3 GB stored** — every index tiles its archive exactly |
| Corpus pass | one command indexes, fits an entry model and emits manifests for all 22 archives in **4 minutes** |
| Entry manifests | **188,298 entries** with exact boundaries across 14 archives (packs whose count verifies exactly) |
| `core_bvh4` | **1,253 of 1,261 packs** whose declared count is reproduced exactly; 109,301 entries |
| Audio | **93,344 Opus + 1,818 XMA2 + 73 ACE1** streams, zero failures; every stream reaches its declared length |
| Names | one registry of **36,952** hash→name pairs, with a flag for JOAAT collisions |
| Script schema | `PSIN` decoded in `script.rpf` (62,910 typed rows, 25 properties + 515 keys named); `LSNS` is a table of 16-byte records. `PSIN` is a general envelope — ≈18,637 records in ten archives — but the property array exists in one file |
| GPU | shader decompilation lives in its own repository, [`rdna2-spirv`](rdna2-spirv/) |

## What is solved, and what is not

**Solved.** Payload coverage and verification for the whole corpus; entry
boundaries for 14 archives; the `core_bvh4` descriptor format; the `ADAT` audio
container including Opus, XMA2 and PCM; the `PSIN`/`LSNS` script schema; a merged
name registry; and the archive/stream accounting above.

**Not solved, and why.** The RPF9 **table of contents is encrypted**, so there are
no original file names or paths — everything here is payload-derived and
offset-addressed. The compiled script bytecode is not in a plaintext section, and
the 331 KB blob in `script.rpf` is masked. Both need the game executable or a PC
build, not more effort.

Details and the failures that led here are in [investigation.md](investigation.md);
open work is in [plan.md](plan.md).

## Checking the repository

```bash
tools/check.sh          # analysis tests, index invariants, shader suite, docs build
tools/check.sh --fast   # skip the docs build and the shader suite
```

Tools run through **uv** (`pyproject.toml`, `uv.lock`), so their dependencies
(numpy for the XMA2 wrapper) are declared rather than assumed. Anything needing
the source archives reports `skipped` instead of failing, so a fresh clone still
gets a meaningful answer.

## Using the names

```bash
python3 tools/name_registry.py --build            # rebuild from every name table
python3 tools/name_registry.py --lookup 0x01166164
python3 tools/name_registry.py --annotate handoff/script-bones.tsv \
    --column bone_hash --out handoff/script-bones-named.tsv
python3 tools/annotate_handoff.py                 # every handoff table at once
```

`handoff/names.tsv` is `hash, name, kind, confidence, source, also_known_as,
ambiguous`, with confidence `curated > meta > grammar > corpus > candidate`. Where
two real strings share a 32-bit JOAAT the row is marked ambiguous rather than
picking one.

## The corpus pass

```bash
tools/corpus_pass.sh /home/lynxnathan/gta6-source --entries
python3 tools/corpus_table.py
python3 tools/corpus_report.py --write docs/extraction/corpus.md
```

It indexes each `*.rpf`, fits the entry models per pack (`single`, `pairs`,
`chains`, `structs-1`, `pos-pairs`) and, with `--entries`, emits a manifest for the
unit the archive's stream/declared ratio implies. The result is
[`docs/extraction/corpus.md`](docs/extraction/corpus.md).

## Single-purpose tools

```bash
python3 tools/stream_index.py ARCHIVE --out output/index/name.tsv
python3 tools/extract_entry.py --archive A --kind zlib --start 0x0 --end 0x1000 --output out.bin
python3 tools/psin_extract.py script.rpf           # PSIN schema from the archive
python3 tools/psin_segment.py --describe 1054      # a script's records, as entries
python3 tools/awc_chunk_table.py FILE              # ADAT chunk table for any variant
python3 tools/lsns_tables.py                       # LSNS tables and record counts
```

The Rust CLI in `src/` covers inspection, pack mapping and partition work:

```bash
cargo build && target/debug/rage-tools-vi --help
```

## Layout

| Path | Purpose |
| --- | --- |
| `src/` | Rust CLI: inspect, map, packs, partition, sections, extract |
| `tools/` | Python indexing, extraction, verification, naming and format probes |
| `handoff/` | Verified manifests and measurements — see [handoff/README.md](handoff/README.md) |
| `docs/` | MkDocs Material site with Mermaid diagrams |
| `tests/` | Smoke tests over the committed data |
| `plan.md` | Live check/todo list |
| `investigation.md` | Append-only research journal |
| `rdna2-spirv/` | Submodule: RDNA2 shader decompiler (separate repository) |

## Data layout

Two disks, two jobs, forced by arithmetic:

| Disk | Holds |
| --- | --- |
| local NVMe, `/home/lynxnathan/gta6-source` (209 GB) | the source archives, so passes read at disk speed |
| Mammoth volume, `output/` | extraction output, manifests and chosen artifacts |

Decoded payload for the whole corpus is 365 GB and fits on neither disk (77 GB
local + 201 GB on Mammoth), so extraction **streams**: decompress, measure, keep
the manifest, discard the bytes. `*.rpf`, `output/`, `cache/`, `site/` and
`target/` are local-only and ignored; manifests and their hashes are committed.

## Prior art and credits

| Project | What this repository uses |
| --- | --- |
| [ItsNotRexed/Leonida](https://github.com/ItsNotRexed/Leonida) | the `ADAT` layout — `tools/awc_parse.py` implements it and cites it |
| [TrinitronClient/GTA6-Asset-Info](https://github.com/TrinitronClient/GTA6-Asset-Info) | byte-level notes on `PSIN`/`LSNS` framing and the object graph |
| [dexyfex/CodeWalker](https://github.com/dexyfex/CodeWalker) | the metadata name table used as a hash vocabulary |
| [GPUOpen isa_spec_manager](https://github.com/GPUOpen-Tools/isa_spec_manager) | the machine-readable RDNA2 ISA behind `rdna2-spirv` |

Where those notes contradicted this project's earlier conclusions, the journal
records the correction instead of quietly changing the number.

## License

MIT — see [LICENSE](LICENSE).
