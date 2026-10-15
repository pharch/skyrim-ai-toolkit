# Imported legacy research provenance

Research imported from the original local `skyrim` repository uses snapshot ID `LEGACY-20261014-A`; its original Git commit was unavailable. Resolve the source checkout only through the ignored `LEGACY_SKYRIM_REPO` binding in `config/local.env`. No machine-specific source path is committed here.

`research/EVIDENCE.json` retains 108 individually hashed legacy source records. `research/LEGACY_SOURCE_PROVENANCE.tsv` maps source-relative paths, SHA-256 values, and evidence IDs. The complete historical `EXP-0001`–`EXP-0005` and `EXP-0007` Markdown dossiers are retained verbatim under `experiments/`; each file's source hash is checked against that provenance table. No `EXP-0006` source document was present in the imported inventory. These experiment records are historical source material, not current test authorization.

Imported reports remain historical evidence. Their stated build, plugin corpus, raw artifacts, and runtime conditions are not promoted to current observations. Claims, mechanisms, contradictions, and frontier entries retain their own scope and uncertainty. Raw game saves, native exports, and private community content were not copied into this repository.
