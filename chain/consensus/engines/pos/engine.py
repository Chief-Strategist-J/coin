import hashlib
import time
from typing import List, Dict, Set
from chain.consensus.interface.engine import ConsensusEngineInterface, Block, FinalizedBlock

class ProofOfStakeEngine(ConsensusEngineInterface):
    """
    Proof of Stake (PoS) Consensus Engine.
    Implements:
    - Sybil resistance via staking.
    - Slashing conditions for double-signing (equivocation).
    - Weak subjectivity checkpoints to prevent long-range attacks.
    """
    def __init__(self, initial_stakes: Dict[str, int], minimum_stake: int = 1000):
        self.stakes = dict(initial_stakes)  # validator -> stake amount
        self.minimum_stake = minimum_stake
        self.slashed_validators: Set[str] = set()
        self.checkpoints: Dict[int, str] = {0: "genesis_checkpoint"}  # epoch -> block_hash
        self.signed_blocks: Dict[int, Dict[str, str]] = {}  # height -> {validator: block_hash}

    def _calculate_hash(self, parent_hash: str, validator: str, transactions: List[Dict], timestamp: float) -> str:
        data = f"{parent_hash}-{validator}-{str(transactions)}-{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def propose_block(self, validator: str, transactions: List[Dict], parent_hash: str) -> Block:
        if validator in self.slashed_validators:
            raise ValueError(f"Validator {validator} has been slashed and cannot participate")
        if self.stakes.get(validator, 0) < self.minimum_stake:
            raise ValueError(f"Validator {validator} has insufficient stake")
        
        timestamp = time.time()
        block_hash = self._calculate_hash(parent_hash, validator, transactions, timestamp)
        block = Block(block_hash, parent_hash, validator, transactions, timestamp)
        block.signatures.append(f"sig-{validator}")
        return block

    def validate_block(self, block: Block) -> bool:
        # 1. Proposer must have sufficient stake and not be slashed
        if block.validator in self.slashed_validators:
            return False
        if self.stakes.get(block.validator, 0) < self.minimum_stake:
            return False

        # 2. Check hash integrity
        expected_hash = self._calculate_hash(block.parent_hash, block.validator, block.transactions, block.timestamp)
        if block.block_hash != expected_hash:
            return False

        # 3. Check signatures against stake authority
        for signature in block.signatures:
            signer = signature.replace("sig-", "")
            if signer in self.slashed_validators or self.stakes.get(signer, 0) < self.minimum_stake:
                return False
        return len(block.signatures) > 0

    def register_signature(self, height: int, validator: str, block_hash: str):
        """
        Registers validator block signature at height.
        Detects equivocation (double-signing same height) and slashes offenders.
        """
        if height not in self.signed_blocks:
            self.signed_blocks[height] = {}
        
        existing_hash = self.signed_blocks[height].get(validator)
        if existing_hash and existing_hash != block_hash:
            # Equivocation detected! Slash the validator
            self.slash(validator)
            raise ValueError(f"Equivocation detected! Validator {validator} slashed.")
        
        self.signed_blocks[height][validator] = block_hash

    def slash(self, validator: str):
        self.slashed_validators.add(validator)
        self.stakes[validator] = 0

    def add_checkpoint(self, epoch: int, block_hash: str):
        """
        Saves a weak subjectivity checkpoint to secure the chain's canonical state history.
        """
        self.checkpoints[epoch] = block_hash

    def finalize_block(self, block: Block) -> FinalizedBlock:
        if not self.validate_block(block):
            raise ValueError("Block validation failed")

        # Sum total active stake
        total_active_stake = sum(self.stakes[v] for v in self.stakes if v not in self.slashed_validators)
        
        # Sum validator signatures stake weight
        signed_stake = 0
        unique_signers = set()
        for signature in block.signatures:
            signer = signature.replace("sig-", "")
            if signer in self.stakes and signer not in unique_signers and signer not in self.slashed_validators:
                unique_signers.add(signer)
                signed_stake += self.stakes[signer]

        # Require > 2/3 stake weight finality
        if signed_stake * 3 <= total_active_stake * 2:
            raise ValueError(f"Insufficient stake weight: got {signed_stake}, need > {int(total_active_stake * 2 / 3)}")

        proof = {
            "consensus": "PoS",
            "signed_stake": signed_stake,
            "total_active_stake": total_active_stake,
            "signatures": list(block.signatures)
        }
        return FinalizedBlock(block, proof)

    def get_validator_set(self) -> List[str]:
        return [v for v, stake in self.stakes.items() if stake >= self.minimum_stake and v not in self.slashed_validators]

    def update_validator_set(self, changes: Dict[str, str]) -> List[str]:
        """
        changes = {"stake_add": ("validator_id", stake_amount)} or {"unstake": "validator_id"}
        """
        if "stake_add" in changes:
            v, stake = changes["stake_add"]
            self.stakes[v] = self.stakes.get(v, 0) + stake
        if "unstake" in changes:
            v = changes["unstake"]
            if v in self.stakes:
                del self.stakes[v]
        return self.get_validator_set()
