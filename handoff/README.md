# handoff artifacts

Verified data products: manifests, name tables and measurements.
Every file is regenerable from the committed tools plus the source
archives, which stay local. `tools/check.sh` verifies that the tools
still agree with these files.

| File | Rows | Columns |
| --- | ---: | --- |
| `archive-inventory-summary.tsv` | 33 | `archive`, `kind`, `ranges`, `stored_bytes`, `decoded_bytes` |
| `audio-ace1-decode.tsv` | 73 | `path`, `stream`, `rate`, `declared_taps`, `data_offset`, `data_bytes`, … (13 total) |
| `audio-awc-framing.tsv` | 2,320 | `path`, `version`, `flags`, `streams`, `data_offset`, `stream`, … (18 total) |
| `audio-full.tsv` | 95,162 | `container`, `stream`, `codec`, `channels`, `frames`, `declared`, … (10 total) |
| `audio-opus-decode.tsv` | 2,081 | `path`, `stream`, `sub_id`, `source_rate`, `output_rate`, `declared_samples`, … (16 total) |
| `audio-opus-trim-model.tsv` | 2,081 | `path`, `stream`, `channels`, `source_rate`, `decoded_frames`, `declared_samples`, … (10 total) |
| `audio-variant-decode.tsv` | 4,704 | `container`, `stream`, `packets`, `channels`, `frames`, `declared`, … (9 total) |
| `audio-xma2-decode.tsv` | 166 | `path`, `stream`, `codec`, `rate`, `samples`, `channels`, … (10 total) |
| `bone-hash-names-curated.tsv` | 60 | `bone_hash`, `name`, `root_id`, `bone_index` |
| `bone-hash-names.tsv` | 99 | `bone_hash`, `name`, `root_id`, `bone_index` |
| `bulk-extraction-status.tsv` | 1 | `archive`, `streams`, `stored_bytes`, `decoded_bytes`, `workers`, `wall_s`, … (9 total) |
| `bulk-extraction-verification-summary.tsv` | 2 | `archive`, `manifest`, `index`, `missing`, `extra`, `failures`, … (7 total) |
| `core-bvh4-descriptors.tsv` | 269,106 | `stream`, `allocated`, `pair_lo`, `pair_hi`, `id0`, `id1`, … (15 total) |
| `core-bvh4-entries.tsv` | 294,614 | `pack`, `entry`, `shape`, `declared_count`, `declared_ok`, `stream`, … (10 total) |
| `corpus-pass.tsv` | 22 | `archive`, `ranges`, `zlib`, `declared`, `stored_bytes`, `packs`, … (9 total) |
| `data-entries-chains.tsv` | 6,537 | `pack`, `entry`, `declared_count`, `delta`, `struct_stream`, `struct_bytes`, … (8 total) |
| `data-skeleton-family-links.tsv` | 16 | `family`, `roots`, `core_bones`, `union_bones`, `root_resource_hits`, `core_part_hits`, … (8 total) |
| `downloads-corpus-inventory.tsv` | 108 | `relative_path`, `stored_bytes`, `rpf_magic_hex`, `extraction_manifest` |
| `entry-reconciliation.tsv` | 22 | `archive`, `packs`, `declared`, `continuations`, `items`, `nested`, … (7 total) |
| `extraction-coverage-summary.tsv` | 8 | `archive`, `file_bytes`, `ranges`, `mapped_bytes`, `coverage`, `decoded_bytes`, … (8 total) |
| `extraction-entry-verification.tsv` | 6 | `archive`, `kind`, `start`, `end`, `expected_bytes`, `actual_bytes`, … (8 total) |
| `extraction-inventory-summary.tsv` | 127 | `archive`, `kind`, `ranges`, `stored_bytes`, `decoded_bytes`, `extracted` |
| `header-census-full.tsv` | 4,373 | `archive`, `offset`, `mode`, `version`, `count`, `front_end`, … (10 total) |
| `header-census.tsv` | 71 | `archive`, `offset`, `mode`, `version`, `count`, `front_end`, … (10 total) |
| `header-words.tsv` | 4,373 | `archive`, `offset`, `mode`, `version`, `count`, `front_end`, … (34 total) |
| `name-coverage.tsv` | 25 | `file`, `rows`, `hash_columns`, `columns_named`, `values_named`, `values_total`, … (7 total) |
| `names.tsv` | 36,952 | `hash`, `name`, `kind`, `confidence`, `source`, `also_known_as`, … (7 total) |
| `navmeshes-entries-chains.tsv` | 25,981 | `pack`, `entry`, `declared_count`, `delta`, `struct_stream`, `struct_bytes`, … (8 total) |
| `navmeshes-entries.tsv` | 2,447 | `pack`, `entry`, `declared_count`, `delta`, `struct_stream`, `struct_bytes`, … (8 total) |
| `pack-extents-leaves.tsv` | 45 | `archive`, `offset`, `count`, `units`, `end`, `unit` |
| `pack-extents-textures.tsv` | 21 | `archive`, `offset`, `count`, `structs`, `children`, `direct`, … (9 total) |
| `pack-model-fit.tsv` | 3,467 | `archive`, `pack`, `declared`, `streams`, `structs`, `chains`, … (7 total) |
| `packs-0f000080-probe.tsv` | 62 | `metric`, `value`, `count` |
| `packs-4042-classes.tsv` | 20 | `size`, `streams`, `entropy`, `zero_fraction`, `adjacent_equal` |
| `packs-4042-probe.tsv` | 64 | `metric`, `value`, `count` |
| `packs-binary-clusters.tsv` | 32 | `cluster`, `streams`, `avg_bytes`, `min_bytes`, `max_bytes`, `top_head`, … (8 total) |
| `packs-label-queue.tsv` | 128 | `cluster`, `rank`, `start`, `decoded_bytes`, `head_after_zeros`, `zero_offset`, … (9 total) |
| `packs-signature-summary.tsv` | 8 | `kind`, `streams`, `decoded_bytes` |
| `psin-entries.tsv` | 4,968 | `psin`, `pair`, `field_a`, `value_a`, `field_b`, `value_b` |
| `psin-names.tsv` | 544 | `kind`, `hash`, `name`, `records`, `types` |
| `psin-segments.tsv` | 5,411 | `psin`, `start_row`, `rows`, `width`, `agreement` |
| `psin-vocabulary.tsv` | 80 | `value`, `group`, `records` |
| `remaining-archive-index-sha256.tsv` | 8 | `archive`, `index`, `index_bytes`, `sha256` |
| `remaining-archive-index-summary.tsv` | 8 | `archive`, `stored_bytes`, `spans`, `zlib`, `decoded_bytes`, `unclassified`, … (10 total) |
| `remaining-archive-index-verification.tsv` | 8 | `archive`, `source_bytes`, `index_stored_bytes`, `status`, `zlib`, `decoded_bytes`, … (7 total) |
| `rig-names-corpus.tsv` | 12 | `hash`, `name`, `kind`, `root_id`, `index`, `shape` |
| `script-array-inventory.tsv` | 7,960 | `root_record`, `root_id`, `root_name`, `root_class`, `root_type`, `array_record`, … (10 total) |
| `script-bone-geometry.tsv` | 3,043 | `root_id`, `root_class`, `table_record`, `bone_index`, `bone_hash`, `points`, … (20 total) |
| `script-bone-namespace-probe.tsv` | 16 | `family`, `roots`, `exact_templates`, `ordered_templates`, `core_bones`, `union_bones`, … (13 total) |
| `script-bone-points.tsv` | 15,732 | `root_record`, `root_id`, `root_class`, `table_record`, `bone_index`, `bone_hash`, … (15 total) |
| `script-bone-roots-named.tsv` | 44 | `root_id`, `bones`, `named`, `families` |
| `script-bone-template-families.tsv` | 16 | `family_id`, `root_count`, `roots`, `min_bones`, `max_bones`, `core_bones`, … (11 total) |
| `script-bone-templates.tsv` | 38 | `template_id`, `bone_count`, `root_count`, `roots`, `hash_signature` |
| `script-bones-named.tsv` | 3,043 | `root_record`, `root_id`, `root_class`, `root_type`, `table_record`, `bone_index`, … (17 total) |
| `script-bones.tsv` | 3,043 | `root_record`, `root_id`, `root_class`, `root_type`, `table_record`, `bone_index`, … (14 total) |
| `script-pair-arrays.tsv` | 7,630 | `root_record`, `root_id`, `root_name`, `root_class`, `root_type`, `array_record`, … (9 total) |
| `script-quadtree-summary.tsv` | 44 | `root_id`, `items`, `nodes`, `max_depth`, `x0`, `y0`, … (8 total) |
| `script-quadtree-verification.tsv` | 8 | `metric`, `value`, `status` |
| `script-skeleton-0x48dcbb01.tsv` | 34 | `bone_index`, `bone_hash`, `name` |
| `script-vehicle-branch-relations.tsv` | 23 | `root_name`, `key_hash`, `key_name`, `array_record`, `points`, `t_end`, … (8 total) |
| `script-vehicle-curve-join.tsv` | 1,935 | `root_id`, `root_name`, `key_hash`, `key_name`, `subtree_records`, `rotation_leaves`, … (8 total) |
| `script-vehicle-curve-points.tsv` | 6,298 | `root_id`, `root_name`, `array_record`, `key_hash`, `key_name`, `point_index`, … (10 total) |
| `script-vehicle-curve-quantization.tsv` | 147 | `axis`, `key_hash`, `grid_deg`, `samples`, `observed_lt_0.05`, `baseline_mean`, … (7 total) |
| `script-vehicle-curves.tsv` | 1,935 | `root_id`, `root_name`, `array_record`, `key_hash`, `key_name`, `points`, … (12 total) |
| `script-vehicles.tsv` | 385 | `root_record`, `root_id`, `root_name`, `flags`, `curve_count`, `channels` |
| `shared-minigame000-bvh4-descriptors.tsv` | 1,233 | `stream`, `allocated`, `pair_lo`, `pair_hi`, `id0`, `id1`, … (15 total) |
| `story000-awc-framing.tsv` | 245 | `path`, `version`, `flags`, `streams`, `data_offset`, `stream`, … (18 total) |
| `story000-awc-variants.tsv` | 2,952 | `path`, `flags`, `streams`, `data_offset`, `chunks`, `seven_per_stream`, … (14 total) |
| `story000-bvh4-control.tsv` | 4 | `start`, `end`, `stored_bytes`, `decoded_bytes`, `sha256`, `xml_root`, … (8 total) |
| `struct-harvest.tsv` | 1,590 | `archive`, `stream`, `kind`, `decoded`, `self_pointers`, `external`, … (10 total) |
| `struct-summary.tsv` | 22 | `archive`, `packs`, `streams`, `entries`, `streams_per_entry`, `sampled`, … (12 total) |
| `textures-entries-chains.tsv` | 25 | `pack`, `entry`, `declared_count`, `delta`, `struct_stream`, `struct_bytes`, … (8 total) |
| `textures-entries.tsv` | 1,349 | `pack`, `entry`, `declared_count`, `delta`, `struct_stream`, `struct_bytes`, … (8 total) |
| `unclassified-summary.tsv` | 7 | `archive`, `ranges`, `bytes`, `largest_span`, `largest_start` |
| `weight-hash-candidates.tsv` | 1 | `weight_hash`, `name`, `shape`, `roots`, `pairs`, `evidence`, … (7 total) |
| `weight-hash-names.tsv` | 21 | `weight_hash`, `name` |
| `anim-index-pilot.md` | — | notes |
| `audio-awc-decode.md` | — | notes |
| `audio-awc.md` | — | notes |
| `data-awc-ace1-ir.md` | — | notes |
| `data-awc-opus-exceptions.md` | — | notes |
| `data-awc-opus.md` | — | notes |
| `data-awc-trim-ace1.md` | — | notes |
| `data-last-child.md` | — | notes |
| `data-skeleton-family-status.md` | — | notes |
| `extraction-coverage.md` | — | notes |
| `extraction-pilot.md` | — | notes |
| `packs-0f000080-probe.md` | — | notes |
| `packs-4042-classes.md` | — | notes |
| `packs-4042-probe.md` | — | notes |
| `packs-binary-clusters.md` | — | notes |
| `packs-semantic-log.md` | — | notes |
| `remaining-archive-index.md` | — | notes |
| `script-bone-namespace-probe.md` | — | notes |
| `script-status.md` | — | notes |
| `story000-bvh4-control.md` | — | notes |
| `story000-bvh4-entry-proof.md` | — | notes |
| `texture-bc7-control.md` | — | notes |
| `texture-mip-tail-blocker.md` | — | notes |
| `texture-trophy-control.md` | — | notes |
| `unclassified-gaps.md` | — | notes |

## Producing tools

| Product | Tool |
| --- | --- |
| names.tsv, name-coverage.tsv | `tools/name_registry.py --build, tools/annotate_handoff.py` |
| psin-*.tsv | `tools/psin_extract.py, tools/psin_entries.py, tools/psin_segment.py` |
| bone-hash-names*.tsv, rig-names-corpus.tsv | `tools/bone_name_probe.py, tools/rig_name_corpus_probe.py` |
| weight-hash*.tsv | `tools/rig_name_corpus_probe.py` |
| pack-model-fit.tsv | `tools/pack_model_fit.py` |
| entry manifests (*-entries*.tsv) | `tools/pair_entry_manifest.py` |
| index and extents tables | `tools/stream_index.py, tools/pack_extents.py, tools/frontb_stride.py` |
| audio tables | `tools/awc_framing_ff02.py, tools/extract_awc_ff02.py` |
| header census | `tools/header_census.py` |
