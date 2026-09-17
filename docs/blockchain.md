# Blockchain foundation: research artifact anchoring (v1)

**Status:** development scaffold, not deployed or audited. Existing physics and
Vireax code is unchanged. This design uses an existing EVM chain rather than
claiming that a hash-linked local file is a decentralized consensus network.

## Boundary and threat model

`research output -> SHA-256 commitment -> local JSON receipt -> optional EVM anchor`

The receipt captures a digest and length of *raw bytes*, never the artifact itself,
its path, wallet keys, model parameters, or personal data. Domain separation:

```
SHA256(UTF8("civilisation.one/artifact/v1") || 0x00 || raw_file_bytes)
```

The `0x`-prefixed 32-byte result is passed directly to `ArtifactAnchor.anchor`.
The contract does **not** calculate SHA-256, verify scientific claims, identify
physical devices, confirm file availability, establish copyright, or attest to
who originally created the artifact. Its `publisher` is merely `msg.sender`.
Anyone may submit and pay transaction fees; each address may anchor a given
digest once. Others may independently anchor the same digest. Records cannot
be edited through the contract. Chain reorgs/finality, contract address, and
chain ID must be considered when verifying a transaction. A standalone receipt
only detects changes relative to its own digest; an independently trusted
on-chain record is required to establish a third-party timestamp.

SHA-256 protects against accidental/intentional alteration only under its
standard collision/second-preimage assumptions. Public digests of predictable
private files may reveal information through guessing: do not anchor sensitive
artifacts without a separate privacy design (e.g., salted commitments).

## Local use: no wallet or RPC required

From the repository root, after `pip install -r requirements.txt pytest`:

```bash
python -m scripts.artifact_receipt create \
  --artifact outputs/vireax_research_log.json \
  --receipt outputs/vireax_research_log.receipt.json
python -m scripts.artifact_receipt verify \
  --artifact outputs/vireax_research_log.json \
  --receipt outputs/vireax_research_log.receipt.json
python -m pytest tests/test_blockchain_commitments.py -v
```

Generate the output with its existing Vireax script first. The receipt creator
will not overwrite an existing receipt. To re-anchor a changed file, choose a
new receipt path and check the new digest. Verification exit codes: `0` match,
`1` mismatch, `2` invalid input/receipt. Do not treat a receipt as an on-chain
transaction: it is not one.

## EVM contract development / optional testnet

Use [Foundry](https://book.getfoundry.sh/) with a **separately provisioned**
test account and an RPC endpoint for an explicitly chosen testnet:

```bash
forge test
forge build
# Review chain ID, RPC URL, account, gas, verified source, and deployment plan.
# Only then deploy with your preferred wallet or deployment pipeline.
```

Deployment, signing, chain selection, contract verification, explorer links, and
transaction confirmation are intentionally not automated. Never commit private
keys, seed phrases, RPC credentials, or production wallet configuration. Do
not use a mainnet until audited and explicitly authorized. After deployment,
record the chain ID, contract address, publishing address, transaction hash,
block number, and finality policy outside the receipt. Verify the digest in
the contract under the **publishing address** and compare against a freshly
calculated local digest. The `anchors(publisher, digest)` getter returns
`(timestamp, exists)`; check `exists` explicitly, even if a test chain has
timestamp zero.

## Next engineering milestones

1. Select an EVM testnet, record chain ID and reorg/finality thresholds, deploy
   and verify bytecode and source with a controlled account.
2. Build an RPC adapter with explicit chain-ID checks, transaction receipts,
   retry/idempotency handling, and read-only verification (never auto-sign).
3. Design DePIN device identity and signed measurements, anti-replay nonces,
   timestamp windows, revocation, and adversarial proof-of-service tests.
4. Add content-addressed off-chain storage and availability checks; only then
   consider batch Merkle roots, rewards, or governance with a security review.

No token issuance, fundraising, wallet custody, bridge, or mainnet deployment
is included in this foundation.
