# MigrationProof submission

Category: standalone Intelligent Contract.

MigrationProof verifies database migration integrity against immutable schemas, baseline snapshots and compatibility rules. It authenticates commit-pinned scripts and test evidence with raw SHA-256 and byte lengths, deterministically checks schemas, counts, uniqueness, nulls, foreign keys and integer sums, then uses independent GenLayer validator reasoning for semantic transformations and rollback requirements. Outcomes are VERIFIED, CONDITIONAL, BREAKING and INCONCLUSIVE. A separate reviewer can append one evidence-backed challenge; adjudication preserves the original receipt history. Evidence and model failures fail closed, retries are bounded, and receipts are hash-linked and domain-bound. The contract assesses supplied evidence and does not execute SQL or claim unseen production data is correct.

## Review links

- [Source](https://github.com/haris4587/MigrationProof/blob/main/contracts/migration_proof.py)
- [Tests](https://github.com/haris4587/MigrationProof/blob/main/tests/test_contract.py)
- [GenVM validation](https://github.com/haris4587/MigrationProof/blob/main/evidence/lint.json)
- [Schema](https://github.com/haris4587/MigrationProof/blob/main/evidence/schema.json)
- [Reproducible SQLite evidence](https://github.com/haris4587/MigrationProof/blob/main/scripts/build_fixtures.py)
- [Security](https://github.com/haris4587/MigrationProof/blob/main/SECURITY.md)
- [Live deployment status](https://github.com/haris4587/MigrationProof/blob/main/docs/DEPLOYMENT.md)

Add only a verified explorer contract URL and successful live review evidence from DEPLOYMENT.md. Offline tests are not live transaction evidence.
