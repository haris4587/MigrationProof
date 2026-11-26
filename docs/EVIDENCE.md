# Evidence format and reproduction

`fixtures/policy.json` and `fixtures/bundle.json` are complete executable examples. Regenerate with `python scripts/build_fixtures.py`; only synthetic in-memory SQLite data is used. The generator asserts transformed values and equality of restored rows with original rows.

## Policy

A policy contains exactly `before_schema`, `after_schema`, `before_rows_hash`, `checks`, and `rules`. A schema maps table names to column/type maps; types are `int`, `str`, `bool`, with nullable values allowed until a not-null check is specified. The baseline hash covers canonical JSON of the full `before_rows` mapping, including row order.

Every deterministic check has `id`, `kind`, `table`, `column`, `target`, `expected`. Kinds: `count`, `not_null`, `unique`, `foreign_key`, `sum`. Count uses empty column; only foreign_key uses a two-item `[table,column]` target. Non-null, uniqueness and FK checks expect zero violations. Sum accepts signed integer expectations; count expects a nonnegative integer. The internal IDs `baseline`, `before_schema`, `after_schema` are reserved.

Every semantic rule has a unique `id`, a precise `requirement`, and `severity` (`mandatory` or `advisory`). At least one mandatory rule is required. Lock the intended compatibility scope and edge cases explicitly rather than asking the model to infer them.

## Bundle and manifest

A bundle contains exactly `before_schema`, `after_schema`, `before_rows`, `after_rows`, `script`, `tests`. Snapshots are table-to-row-array mappings with exact columns. Migration scripts and test evidence are embedded in the bundle, so the commit pin and raw digest bind them together.

After committing the evidence, build a manifest with:

```sh
python scripts/manifest.py FULL_40_CHARACTER_COMMIT fixtures/bundle.json
```

This prints JSON containing `url`, `sha256`, `bytes`. Hash and byte count cover the raw UTF-8 file, including any newline. Submit this exact JSON string. Counterevidence uses the same manifest format and approved publisher, pointing at a plain UTF-8 file. It supplements the locked original bundle; it cannot replace rows or silently change requirements.

## Receipt hashes

Canonical JSON is Python `json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)` encoded as UTF-8. A receipt wrapper has `receipt` and `hash`; recompute SHA-256 over the canonical `receipt` object only. Each receipt references the preceding hash, sequence, case ID, chain ID, contract address, actor and event. REVIEW/ADJUDICATE data includes policy hash, manifests, attempt and full decision. The case head identifies the latest receipt. No receipt is overwritten.

For an exported array of receipt wrappers:

```sh
python scripts/verify_receipts.py receipts.json
```

This validates the hash chain and consistent domain/sequence. Compare its final head with a trusted `get_case` read; a standalone chain can be re-created by an attacker and is not a substitute for authentic on-chain state.
