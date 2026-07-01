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
