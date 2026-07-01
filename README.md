# Decentralized AI Agent Network & DEX Core

This is a trustless blockchain platform designed to let **AI Agents** interact, trade tokens, and coordinate with each other securely and without relying on a central authority.

---

## 🚀 How It Works (For End Users)

### 1. Peer-to-Peer (P2P) Network
Nodes in this network gossip messages and coordinate transactions. To prevent spam and malicious actions, nodes track a **Reputation Score** for each peer. If a node begins misbehaving, its reputation drops, and other nodes automatically stop accepting messages from it.

### 2. Trustless Consensus (PoA & PoS)
The network stays secure and consistent using two built-in consensus engines:
* **Proof-of-Authority (PoA)**: Used for testnets. Authorized validators propose blocks, requiring a $2/3$ signature agreement threshold.
* **Proof-of-Stake (PoS)**: Used for mainnets. Validators lock up coins (stake) to validate blocks. If a validator attempts to cheat by signing two conflicting blocks at the same time, the protocol detects this immediately and **slashes their stake to zero**.

### 3. Smart Contracts & VM
You can deploy and run programs (Smart Contracts) on the network. The system includes:
* A simulated **EVM execution sandbox** to process transactions.
* **Gas limits and fees** to prevent infinite loops from freezing the network.
* **State Rollbacks**: If a transaction runs out of gas, it reverts to keep your funds safe.

### 4. Layer 2 Rollups & L1 Bridge
To make transactions faster and cheaper, the network supports Layer 2 (L2) Rollups:
* You lock your assets on Layer 1 (L1) via the **Bridge** to use them on L2.
* Validators bundle transactions together and submit them to L1.
* There is a **Challenge Window**. If anyone detects that a validator submitted an invalid transaction, they submit a **Fraud Proof**, which automatically cancels the invalid update.
* Once the challenge window closes unchallenged, you can securely withdraw your funds back to L1.

### 5. AI Agent Communication (ACP)
AI Agents talk to the blockchain using the **Agent Communication Protocol (ACP)**. They send structured messages (envelopes) requesting actions (like trading tokens), and the network processes them and returns cryptographic proofs showing that the action completed successfully.

### 6. Trading (DEX AMM)
There is a built-in Decentralized Exchange (DEX). It uses a **Constant Product formula ($x \times y = k$)** to swap tokens:
* Anyone can add tokens to a liquidity pool to earn fees.
* When you trade Token A for Token B, the pool calculates the price automatically and charges a tiny 0.3% fee to reward the liquidity providers.

---

## 🛠️ Developer Integration & Testing

### How to Run Tests
Run the entire protocol test suite with these commands:

```bash
# Run P2P network tests
python3 -m unittest chain/p2p/transport/test_node.py

# Run Consensus engine tests
python3 -m unittest chain/consensus/engines/poa/test_engine.py
python3 -m unittest chain/consensus/engines/pos/test_engine.py

# Run State Machine and VM execution tests
python3 -m unittest chain/execution/state/test_machine.py

# Run Bridge and Rollup tests
python3 -m unittest chain/l2/bridge/test_bridge.py

# Run AI Agent communication tests
python3 -m unittest chain/rpc/api/test_acp_adapter.py

# Run DEX trading contract tests
python3 -m unittest chain/contracts/core/test_dex.py
```

### How to Build and Run via Docker
This repository conforms to the **Single Artifact Principle** and builds into a single container:

```bash
# 1. Build the docker image
docker build -t coin-protocol-core .

# 2. Run the node and expose the ACP adapter port
docker run -p 8545:8545 coin-protocol-core
```

---

## 🌲 Protocol Business Decision Tree

This protocol is structured to map high-level product and business requirements directly to cryptographic and architectural constraints:

```
[Business Goal: Build a Trustless AI Agent DEX Network]
 ├── [Trust Model: Traditional System -> Decentralized Blockchain]
 │    ├── Pros: Eliminates single operator dependency; auditability guarantees safety.
 │    └── Cons: Higher execution latency; state modifications are irreversible.
 │
 ├── [Consensus selection: Low-latency Testnet vs Secure Mainnet]
 │    ├── Proof-of-Authority (PoA)
 │    │    ├── Pros: Fast block finalization; simple authority sets.
 │    │    └── Cons: Not Byzantine Fault Tolerant under 4 nodes.
 │    └── Proof-of-Stake (PoS)
 │         ├── Pros: Economic Sybil-resistance; self-correcting via slashing.
 │         └── Cons: Risk of long-range history rewrites (mitigated by checkpoints).
 │
 ├── [Scalability strategy: Layer 1 execution vs Layer 2 Rollups]
 │    ├── Layer 1 Base Chain
 │    │    ├── Pros: Direct cryptographic settlement; immediate state finality.
 │    │    └── Cons: Throughput limits; higher execution gas fees.
 │    └── Layer 2 Optimistic Rollup
 │         ├── Pros: High transaction throughput; extremely cheap fees.
 │         └── Cons: 7-day challenge window wait time for withdrawals.
 │
 └── [Interface standard: REST API vs Agent Communication Protocol (ACP)]
      ├── REST HTTP
      │    ├── Pros: Standard web compatibility; simple client implementation.
      │    └── Cons: Missing conversational metadata; no direct agent trace context.
      └── ACP Envelope Boundary
           ├── Pros: Natural integration with multi-agent networks; W3C tracing.
           └── Cons: Payload strictness; stateless mapping translation layers.
```

