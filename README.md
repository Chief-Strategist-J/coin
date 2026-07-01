# Decentralized AI Agent Network & DEX Core

A secure, trustless, and modular blockchain protocol designed for coordinating autonomous AI Agent Networks and executing Decentralized Exchange (DEX) mechanics under Byzantine assumptions.

## Core Architectural Layout

This project follows a decoupled, modular design ensuring that consensus, execution engines, and communication protocols are isolated boundaries:

```
├── chain/
│   ├── p2p/                  # P2P Node transport, discovery, and gossip protocol
│   ├── consensus/            # Pluggable Consensus Engines (PoA, PoS, DPoS)
│   ├── execution/            # State machine (Mempool, Merkle Trie, Block validation)
│   ├── vm/                   # Multi-VM isolation (EVM, WASM runtime)
│   ├── l2/                   # Rollups, Batch Sequencers, and L1 Bridges
│   └── rpc/                  # JSON-RPC Gateway & API endpoints
├── infra/                    # Operational configs (Node deployments, Key KMS, Monitoring)
└── policies/                 # Architectural rules, coupling constraints, and designs
```

---

## What We Have Implemented

### 1. P2P Transport Layer (`chain/p2p/transport`)
* **`Peer` representation**: Tracks node type, address, connection states, and reputation metrics (0–100 scale).
* **`P2PNodeInterface`**:
  * Implements dynamic peer registration.
  * Pub/Sub topic subscription system.
  * **Gossip propagation**: Restricts block/transaction gossiping to healthy, trusted nodes by checking peer reputation status (nodes with `< 20` reputation are filtered out).

### 2. Pluggable Consensus Layer (`chain/consensus`)
* **`ConsensusEngineInterface`**: Standardizes block creation, validation, and finality mechanisms, allowing pluggable consensus swapping (PoA, PoS, DPoS) without modifying the execution layer.
* **`ProofOfAuthorityEngine`**:
  * Implements a BFT-PoA consensus algorithm.
  * Recomputation validation for block hash integrity.
  * **Threshold finality**: Requires greater than `2/3` of the active validator set to sign the block before declaring it finalized.
  * **BFT Safety**: Enforces a strict minimum limit of `4` validators to tolerate up to `1` Byzantine failure.

---

## How to Run & Write Tests

We follow a strict "No network, database, or filesystem access in unit tests" rule to keep tests extremely fast and deterministic.

### Running Existing Unit Tests
To run unit tests for the P2P transport layer and the Proof-of-Authority consensus layer, execute:

```bash
# Run P2P transport layer tests
python3 -m unittest chain/p2p/transport/test_node.py

# Run PoA consensus engine tests
python3 -m unittest chain/consensus/engines/poa/test_engine.py
```

### Adding New Tests
When adding new features (e.g., PoS staking, WASM execution, etc.):
1. Create a corresponding `test_*.py` file next to your implementation.
2. Extend `unittest.TestCase`.
3. Ensure all external dependencies are cleanly mocked out via dependency injection or interfaces.

---

## How to Extend the Protocol

### 1. Swapping Consensus Engines
To introduce Proof-of-Stake (PoS):
1. Subclass the `ConsensusEngineInterface` located in `chain/consensus/interface/engine.py`.
2. Implement custom staking, slashing, and finality checkpoints under `chain/consensus/engines/pos/`.

### 2. Creating New Node Types
To run a specialized node (e.g. an **RPC Node** or **Archive Node**), instantiate the `P2PNodeInterface` with the corresponding `NodeType` configuration:
```python
from chain.p2p.transport.node import P2PNodeInterface, NodeType

rpc_node = P2PNodeInterface(
    node_id="rpc-node-01",
    node_type=NodeType.RPC,
    listen_address="0.0.0.0:8545"
)
```
