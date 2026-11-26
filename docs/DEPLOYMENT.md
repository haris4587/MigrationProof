# Deployment

## Build verification

GenVM linter 0.11.0 validates the pinned runner, contract storage declarations and ABI. The runner pin is intentional for Studio compatibility; the tool reports an informational newer-runner notice. Offline host-double tests and a real SQLite migration/rollback pass. These checks do not establish live deployment or AI consensus.

## Studio procedure

1. Open https://studio.genlayer.com/contracts and use the inbuilt Studio wallet.
2. Import `contracts/migration_proof.py` unchanged.
3. Deploy with publisher `haris4587/MigrationProof` and a nonzero reviewer address different from the deploying wallet. Use a reviewer wallet you control for a full challenge-path test. Do not use a random address for production governance.
4. Use Full Consensus mode. Create a case using `fixtures/policy.json`, then lock, submit its commit-pinned manifest, and review.
5. Read `get_case` and every `get_receipt` entry. Capture the deployment address, transaction hashes, consensus mode, accepted/finalized status, decision and receipt head. Protocol finality and a successful deterministic transaction alone do not prove an LLM review succeeded.
6. Switch to the designated reviewer only to append a counterevidence manifest. Anyone can then trigger adjudication. Preserve both original and subsequent receipts.

## Observed live attempt — 26 November 2026

The exact source was imported into Studio as `migration_proof.py`. The Run and Debug panel showed **Normal (Full Consensus)**, **Not deployed yet**, and **You need at least one validator before you can deploy or interact with a contract.** The Validators panel showed **Validators 0 / No validators**. Studio also returned HTTP 429 for its API, with **Rate limit exceeded: 30 requests per minute**. A refresh did not restore validators or enable deployment.

No deployment transaction was submitted. There is no verified contract address, explorer contract link or successful live semantic verdict to report. The contract remains imported and ready in Studio; live create/lock/submit/review/challenge/adjudication verification is pending restored validator availability. Offline lifecycle tests must not be represented as live evidence.

## Published validation

[GitHub Actions run 45779084919](https://github.com/haris4587/MigrationProof/actions/runs/45779084919) completed successfully for implementation commit `b130821bd9dfbd0d94acc0f73467b807192f22d6`, including all 51 offline tests, deterministic fixture regeneration and GenVM check/schema commands.

The exact fixture manifests are saved in `evidence/bundle-manifest.json` and `evidence/counter-manifest.json`. Both pin the implementation commit; later documentation commits do not change their evidence bytes.

