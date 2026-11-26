# Security and trust model

MigrationProof reviews evidence; it is not a database oracle. The approved publisher can fabricate snapshots or test results. Commit hashes, byte counts and SHA-256 prove byte identity and provenance, not factual truth or completeness. Publish sanitized or synthetic data only: URLs, supplied evidence and verdicts may be public and processed by validator model providers.

## Boundaries

- The owner registers and locks cases. A distinct designated reviewer can append one challenge. Address separation does not prove organizational independence. The publisher repository is fixed at deployment, including counterevidence; production teams must give their reviewer a reliable way to publish independent material there. Owner-controlled publishing may censor evidence. No role transfer is supported.
- Requirements cannot change after creation. Evidence cannot change after submission. Revisions use new case IDs; IDs and receipts include version, chain ID and contract address.
- Evidence URLs are restricted to `https://raw.githubusercontent.com/<locked publisher>/<40 lowercase hex commit>/<safe path>`. No mutable branches, query strings, fragments, percent encoding, credentials, alternate ports, localhost or IP URLs are accepted. GitHub response and redirect behavior is part of the infrastructure trust boundary; the SDK performs the fetch. Byte/hash validation prevents a redirected or substituted body from becoming trusted.
- Accepted bundles are at most 48,000 UTF-8 bytes, JSON has at most 15 nesting levels, arrays at most 200 elements, schemas at most 12 tables and 20 columns, and each table snapshot at most 200 rows. Policies are at most 16,000 bytes; there are 24 deterministic checks and 8 semantic rules maximum. Scripts/tests are at most 12,000 characters each; challenge text at most 12,000 UTF-8 bytes. HTTP body limits are checked after the SDK fetch, not a streaming network cap; runtime resource limits still apply.
- JSON rejects duplicate keys, floats, NaN, infinity, excessive integers and unknown structural fields. Reserved internal check IDs cannot be shadowed. Row values distinguish booleans from integers.
- SQL and evidence are never executed by the contract. Model instructions isolate all evidence as untrusted data and forbid browsing/tool calls. Grounded quotations and independent reassessment reduce prompt injection risk; they do not eliminate model error.
- Every validator independently authenticates evidence and performs the same checks and AI task. It compares all rule statuses and the derived outcome, and validates the leader's exact quotations. Reasons are explanatory text; exact wording is not a consensus field. Identical wrong conclusions remain possible.
- Deterministic constraint failures take precedence over semantic findings. Missing evidence, malformed output and incomplete coverage fail closed. Evidence retrieval failures can agree as INCONCLUSIVE; consensus disagreement instead leaves state unchanged.
- No private keys, credentials, funds, database connection strings, SQL execution, external writes or payouts exist in the contract.

## Limitations

A bounded snapshot does not prove the entire production dataset was migrated, test reports cannot establish execution without external attestation, and declared schema maps omit engine-specific indexes/checks/collations. Foreign keys check membership only; uniqueness on the referenced key must be locked separately. Strings use exact Unicode equality. Snapshot row order affects baseline hashes. Model reasoning can assess compatibility only to the extent the locked rule and evidence describe consumers.

Retries are transaction-level bounded after committed INCONCLUSIVE results. Protocol-level leader rotations and failed transactions are controlled by GenLayer and do not consume contract attempt counters. The one reviewer challenge may remain available indefinitely; this version has no timed finality or automatic deployment gate.

Report reproducible issues privately to the repository owner using GitHub's private security reporting if available. Do not post real database records or credentials in an issue.
