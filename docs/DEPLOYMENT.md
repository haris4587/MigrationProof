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

Live status and any limitations will be recorded here after the deployment attempt. Until a verified address and successful semantic review are recorded, do not describe this repository as live or production verified.
