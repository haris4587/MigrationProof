# MigrationProof

A standalone GenLayer Intelligent Contract that checks database migration integrity and compatibility against immutable requirements and commit-pinned evidence. It combines deterministic snapshot checks with independent validator reasoning about data transformations and rollback behavior.

**Scope:** evidence-grounded verification of bounded snapshots, scripts and test reports. It never connects to a database, executes submitted SQL, or controls a migration. A certificate applies only to the locked requirements and supplied evidence, not an unseen production database.

## Outcomes

Precedence is deterministic; AI cannot override a failed integrity check.

| Outcome | Rule |
|---|---|
| BREAKING | Any deterministic check fails, or any mandatory semantic rule is FAIL |
| INCONCLUSIVE | Evidence is unavailable/invalid, or any semantic rule is UNKNOWN without a demonstrated mandatory failure |
| CONDITIONAL | All mandatory rules pass, no UNKNOWN remains, and at least one advisory rule fails |
| VERIFIED | Every deterministic and semantic requirement passes |

## Contract workflow

Deploy [migration_proof.py](contracts/migration_proof.py) with `publisher` (`owner/repository`) and a nonzero `reviewer` address different from the deploying owner. These roles have no setters.

1. Owner calls `create(title, policy_json)` to register original and expected schemas, a baseline snapshot hash, numeric checks and semantic migration rules. It returns a unique case ID. Requirements are immutable even in DRAFT.
2. Owner calls `lock(case_id)` before evidence submission.
3. Owner calls `submit(case_id, manifest_json)` to bind a single evidence bundle to a full Git commit, exact byte length and SHA-256.
4. Anyone calls `review(case_id)`. Each validator independently fetches and authenticates the evidence, recomputes deterministic checks and reruns semantic analysis. Every rule status and outcome must agree. Leader quotations are independently reauthenticated.
5. The designated reviewer may call `challenge(case_id, counter_manifest_json)` once after a review. Anyone calls `review` again to adjudicate against the original package plus pinned counterevidence. Earlier receipts remain available.

An INCONCLUSIVE result permits up to three review transactions per phase, against the identical package. Substantive outcomes cannot be rerolled. One challenge opens a separate phase with three attempts. Revised scripts or requirements require a new case. Protocol-level consensus failure does not commit state and is separate from a stored INCONCLUSIVE result.

Views: `get_case(case_id)` returns current policy, state, outcome and receipt head; `get_receipt(case_id, sequence)` returns a canonical hash-linked receipt. Sequences start at 1. There is no delete, evidence replacement, payout or administrator override.

## Integrity and compatibility

Deterministic checks support row counts, SQL-style single-column uniqueness, non-null constraints, single-column foreign-key membership, signed integer sums, exact schema maps, and original snapshot authentication. Nulls are excluded from uniqueness and foreign-key checks; add a separate not-null check where required. Sums reject nulls. Composite keys, SQL engines' type/collation behavior and large datasets are outside this version's deterministic scope.

Semantic rules capture requirements that numeric checks cannot establish alone: unit conversion, identity preservation, lossy transforms, rollback guarantees, and client compatibility. Each rule has a locked mandatory/advisory severity. PASS and FAIL require a verbatim source quote. Model errors get one retry, then UNKNOWN; unknown never becomes success.

## Verification status

**Built and published; deployment pending.** All 51 offline tests, SQLite fixture reproduction and GenVM validation/schema extraction pass. [GitHub Actions also passed](https://github.com/haris4587/MigrationProof/actions/runs/45779084919). Studio source import succeeded, but live deployment is unavailable because Studio shows zero validators and API rate-limit errors. No explorer address or live consensus result is claimed. See the exact [deployment status](docs/DEPLOYMENT.md).

## Reproduce

```sh
python -m pip install -r requirements-dev.txt
python scripts/build_fixtures.py
python -m unittest discover -s tests -v
genvm-lint check contracts/migration_proof.py --json
genvm-lint schema contracts/migration_proof.py --json
```

The fixture generator executes a real in-memory SQLite dollars-to-cents migration and rollback, including positive, zero, negative and NULL balances. Offline tests use explicit host doubles for GenLayer APIs; they do not prove live AI consensus. See [verification results](evidence/offline-tests.txt), [GenVM validation](evidence/lint.json), and [ABI schema](evidence/schema.json).

[Evidence format and hashes](docs/EVIDENCE.md) · [Security and trust model](SECURITY.md) · [Deployment and live verification](docs/DEPLOYMENT.md) · [Submission information](docs/SUBMISSION.md)
