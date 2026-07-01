----------------- MODULE ProtocolSpecification -----------------
EXTENDS Naturals, Sequences

VARIABLES 
    validator_set,        \* Set of active authorized validator addresses
    balances,             \* Map of account addresses -> integers
    nonces,               \* Map of account addresses -> nonces
    signed_blocks,        \* Map of height -> (validator -> block_hash)
    slashed_validators,   \* Set of slashed validator addresses
    l1_deposits,          \* Map of user -> deposited L1 balance
    l2_state_batches      \* Sequence of L2 state batches posted to L1

TypeOK ==
    /\ validator_set \subseteq STRING
    /\ balances \in [STRING -> Nat]
    /\ nonces \in [STRING -> Nat]
    /\ slashed_validators \subseteq STRING
    /\ l1_deposits \in [STRING -> Nat]
    /\ l2_state_batches \in Seq([index: Nat, root: STRING, timestamp: Nat])

Init ==
    /\ validator_set = {"val-1", "val-2", "val-3", "val-4"}
    /\ balances = [addr \in {"alice", "bob", "val-1", "val-2", "val-3", "val-4"} -> 10000]
    /\ nonces = [addr \in {"alice", "bob", "val-1", "val-2", "val-3", "val-4"} -> 0]
    /\ signed_blocks = [h \in Nat -> [v \in STRING -> ""]]
    /\ slashed_validators = {}
    /\ l1_deposits = [user \in STRING -> 0]
    /\ l2_state_batches = <<>>

\* 1. L1 State Transition (Transfers)
Transfer(from, to, val, gas) ==
    /\ from \in DOMAIN balances
    /\ to \in DOMAIN balances
    /\ balances[from] >= val + gas
    /\ balances' = [balances EXCEPT ![from] = @ - (val + gas), ![to] = @ + val]
    /\ nonces' = [nonces EXCEPT ![from] = @ + 1]
    /\ UNCHANGED <<validator_set, signed_blocks, slashed_validators, l1_deposits, l2_state_batches>>

\* 2. Proof-of-Stake Equivocation Slashing
RegisterSignature(height, validator, block_hash) ==
    /\ validator \in validator_set
    /\ validator \notin slashed_validators
    /\  IF signed_blocks[height][validator] /= "" /\ signed_blocks[height][validator] /= block_hash
        THEN \* Equivocation detected: Slash!
             /\ slashed_validators' = slashed_validators \cup {validator}
             /\ balances' = [balances EXCEPT ![validator] = 0]
             /\ UNCHANGED <<validator_set, nonces, signed_blocks, l1_deposits, l2_state_batches>>
        ELSE \* Valid signature log
             /\ signed_blocks' = [signed_blocks EXCEPT ![height][validator] = block_hash]
             /\ UNCHANGED <<validator_set, balances, nonces, slashed_validators, l1_deposits, l2_state_batches>>

\* 3. L2 Optimistic Bridge Operations (Deposit & Rollup Commit)
BridgeDeposit(user, amount) ==
    /\ user \in DOMAIN balances
    /\ balances[user] >= amount
    /\ balances' = [balances EXCEPT ![user] = @ - amount]
    /\ l1_deposits' = [l1_deposits EXCEPT ![user] = @ + amount]
    /\ UNCHANGED <<validator_set, nonces, signed_blocks, slashed_validators, l2_state_batches>>

SubmitBatch(state_root, tx_hashes, submitter) ==
    /\ submitter \in validator_set
    /\ submitter \notin slashed_validators
    /\ l2_state_batches' = Append(l2_state_batches, [
            index       |-> Len(l2_state_batches),
            root        |-> state_root,
            timestamp   |-> Len(l2_state_batches) + 1
       ])
    /\ UNCHANGED <<validator_set, balances, nonces, signed_blocks, slashed_validators, l1_deposits>>

=============================================================================
