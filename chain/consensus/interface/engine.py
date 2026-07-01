from typing import List, Dict, Tuple
from abc import ABC, abstractmethod

class Block:
    def __init__(self, block_hash: str, parent_hash: str, validator: str, transactions: List[Dict], timestamp: float):
        self.block_hash = block_hash
        self.parent_hash = parent_hash
        self.validator = validator
        self.transactions = transactions
        self.timestamp = timestamp
        self.signatures: List[str] = []

class FinalizedBlock:
    def __init__(self, block: Block, consensus_proof: Dict):
        self.block = block
        self.consensus_proof = consensus_proof

class ConsensusEngineInterface(ABC):
    """
    Modular Consensus Engine Interface that all engines (PoA, PoS, DPoS) must implement.
    Correctness before execution layer.
    """
    
    @abstractmethod
    def propose_block(self, validator: str, transactions: List[Dict], parent_hash: str) -> Block:
        """
        Creates a candidate block for consensus proposal.
        """
        pass

    @abstractmethod
    def validate_block(self, block: Block) -> bool:
        """
        Validates the block structure, signature verification, and consensus criteria.
        """
        pass

    @abstractmethod
    def finalize_block(self, block: Block) -> FinalizedBlock:
        """
        Marks a block as finalized once consensus threshold rules are satisfied.
        """
        pass

    @abstractmethod
    def get_validator_set(self) -> List[str]:
        """
        Returns the active set of validators authorized for the current epoch/state.
        """
        pass

    @abstractmethod
    def update_validator_set(self, changes: Dict[str, str]) -> List[str]:
        """
        Applies changes to the validator set (adds/removes).
        """
        pass
