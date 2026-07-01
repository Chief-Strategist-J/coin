import hashlib
import time
from typing import List, Dict
from chain.consensus.interface.engine import ConsensusEngineInterface, Block, FinalizedBlock

class ProofOfAuthorityEngine(ConsensusEngineInterface):
    """
    PoA Consensus Engine implementation.
    Consensus requires block proposal from authorized validators and threshold signatures.
    """
    def __init__(self, initial_validators: List[str]):
        self.validators = list(initial_validators)
        self.blocks: Dict[str, Block] = {}

    def _calculate_hash(self, parent_hash: str, validator: str, transactions: List[Dict], timestamp: float) -> str:
        data = f"{parent_hash}-{validator}-{str(transactions)}-{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def propose_block(self, validator: str, transactions: List[Dict], parent_hash: str) -> Block:
        if validator not in self.validators:
            raise ValueError(f"Validator {validator} not in authorized validator set")
        timestamp = time.time()
        block_hash = self._calculate_hash(parent_hash, validator, transactions, timestamp)
        block = Block(block_hash, parent_hash, validator, transactions, timestamp)
        # Author proposer's initial signature
        block.signatures.append(f"sig-{validator}")
        return block

    def validate_block(self, block: Block) -> bool:
        # 1. Proposer must be authorized
        if block.validator not in self.validators:
            return False
        
        # 2. Recompute hash for integrity verification
        expected_hash = self._calculate_hash(block.parent_hash, block.validator, block.transactions, block.timestamp)
        if block.block_hash != expected_hash:
            return False
        
        # 3. Must contain at least one valid signature from an authorized validator
        for signature in block.signatures:
            signer = signature.replace("sig-", "")
            if signer not in self.validators:
                return False
        return len(block.signatures) > 0

    def finalize_block(self, block: Block) -> FinalizedBlock:
        if not self.validate_block(block):
            raise ValueError("Block validation failed; cannot finalize block")
        
        # In BFT-PoA, block is final when > 2/3 (or simple majority) of validators sign it
        required_signatures = (len(self.validators) * 2) // 3 + 1
        if len(block.signatures) < required_signatures:
            raise ValueError(f"Insufficient signatures: got {len(block.signatures)}, need {required_signatures}")
        
        proof = {
            "consensus": "PoA",
            "required_signatures": required_signatures,
            "signatures": list(block.signatures)
        }
        self.blocks[block.block_hash] = block
        return FinalizedBlock(block, proof)

    def get_validator_set(self) -> List[str]:
        return list(self.validators)

    def update_validator_set(self, changes: Dict[str, str]) -> List[str]:
        """
        Updates validator set:
        changes = {"add": "validator_id"} or {"remove": "validator_id"}
        """
        if "add" in changes:
            v_add = changes["add"]
            if v_add not in self.validators:
                self.validators.append(v_add)
        if "remove" in changes:
            v_remove = changes["remove"]
            if v_remove in self.validators:
                if len(self.validators) <= 4:
                    raise ValueError("Cannot reduce validator set below BFT-PoA minimum of 4 validators")
                self.validators.remove(v_remove)
        return self.get_validator_set()
