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
  * Implements dynamic peer registration and topic subscription systems.
  * **Gossip propagation**: Restricts block/transaction gossiping to healthy, trusted nodes (reputation `>= 20`).

### 2. Pluggable Consensus Layer (`chain/consensus`)
* **`ConsensusEngineInterface`**: Standardizes block creation, validation, and finality mechanisms.
* **`ProofOfAuthorityEngine`**: Implements BFT-PoA consensus requiring validator threshold signatures (`> 2/3` validation set) and enforcing a minimum set of `4` validators.
* **`ProofOfStakeEngine`**: Implements economic Sybil resistance, equivocation slashing (double-sign protection), weak subjectivity checkpoints, and stake-weighted block finality.

### 3. L1 Execution Layer & VM (`chain/execution`, `chain/vm`)
* **`VMInterface`**: Standardizes sandbox bytecode execution boundary.
* **`DummyEVM`**: Simulates sandboxed gas-metered execution (SSTORE/SLOAD) and 256-bit safe integer arithmetic.
* **`StateMachine`**:
  * Orchestrates account balances, transaction nonces, gas limits, and transaction execution.
  * Computes deterministic state roots by sorting account storage maps.
  * Reverts contract states and handles gas refunds.

### 4. L2 Rollup & L1 Bridge (`chain/l2`)
* **`L1BridgeContract`**:
  * Accepts deposits locking assets on L1 to be claimed on L2.
  * Publishes L2 state roots via `submit_state_batch` to start the challenge window.
  * Evaluates fraud proofs (`challenge_batch`) to invalidate state root sequences in case of malicious execution.
  * Settles unchallenged L2->L1 withdrawals once the challenge window expires.

### 5. Developer APIs & Agent Protocols (`chain/rpc/api`)
* **`ACPAdapter`**:
  * Implements the Agent Communication Protocol (ACP) for coordinating Agentic Workflows.
  * Parses, validates, and responds to incoming FIPA-style ACP JSON envelopes.
  * Maps agent `REQUEST` performance envelopes directly to State Machine transaction executions.
  * Formats success outputs to structured `INFORM` response schemas containing height details and cryptographic state root validation parameters.

### 6. Decentralized Exchange Smart Contracts (`chain/contracts/core`)
* **`DexMarketMaker`**:
  * Core automated market maker (AMM) implementing Constant Product formula mechanics (`x * y = k`).
  * Manages liquidity provider pools, shares, and reserves.
  * Implements transaction fee deductions (0.3% base cost) on token swaps.

---

## How to Run & Write Tests

We follow a strict "No network, database, or filesystem access in unit tests" rule to keep tests extremely fast and deterministic.

### Running Existing Unit & Integration Tests
To run tests across our consensus, execution, rollup, API, and contract layers, execute:

```bash
# Run P2P transport layer tests
python3 -m unittest chain/p2p/transport/test_node.py

# Run PoA & PoS consensus engine tests
python3 -m unittest chain/consensus/engines/poa/test_engine.py
python3 -m unittest chain/consensus/engines/pos/test_engine.py

# Run L1 state machine & VM integration tests
python3 -m unittest chain/execution/state/test_machine.py

# Run L2 Bridge & Rollup tests
python3 -m unittest chain/l2/bridge/test_bridge.py

# Run ACP Agent protocol tests
python3 -m unittest chain/rpc/api/test_acp_adapter.py

# Run DEX smart contract tests
python3 -m unittest chain/contracts/core/test_dex.py
```

### Adding New Tests
When adding new features (e.g., DPoS delegation, WASM execution, etc.):
1. Create a corresponding `test_*.py` file next to your implementation.
2. Extend `unittest.TestCase`.
3. Ensure all external dependencies are cleanly mocked out via dependency injection or interfaces.

---

## How to Extend the Protocol

### 1. Swapping Consensus Engines
To introduce Delegated Proof-of-Stake (DPoS):
1. Subclass the `ConsensusEngineInterface` located in `chain/consensus/interface/engine.py`.
2. Implement custom validator elections, delegation, and vote-decay rules under `chain/consensus/engines/dpos/`.

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
