from typing import List, Dict, Any, Tuple
import hashlib

class L1BridgeContract:
    """
    L1 Bridge Contract executing on the L1 state machine.
    Manages L1->L2 deposits, L2->L1 withdrawal settlements, and L2 batch commitment verifications.
    """
    def __init__(self, challenge_window: int = 10):  
        self.deposits: Dict[str, int] = {}  
        self.withdrawals: Dict[str, Dict[str, Any]] = {}  
        self.state_batches: List[Dict[str, Any]] = []  
        self.challenge_window = challenge_window
        self.challenges: Dict[int, bool] = {}  

    def deposit(self, user: str, amount: int) -> Dict[str, Any]:
        """
        Locks L1 assets and registers pending balance to be claimed on L2.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.deposits[user] = self.deposits.get(user, 0) + amount
        return {"event": "Deposit", "user": user, "amount": amount}

    def submit_state_batch(self, batch_index: int, state_root: str, tx_hashes: List[str], submitter: str) -> None:
        """
        Publishes the L2 state root batch to L1.
        Starts the challenge window.
        """
        if batch_index != len(self.state_batches):
            raise ValueError("Out of order batch indices")
        
        self.state_batches.append({
            "index": batch_index,
            "state_root": state_root,
            "tx_hashes": tx_hashes,
            "submitter": submitter,
            "timestamp": len(self.state_batches)  
        })

    def challenge_batch(self, batch_index: int, proof_data: str) -> bool:
        """
        Optimistic challenge validation: verification of invalid transactions in L2 batch.
        """
        if batch_index >= len(self.state_batches):
            raise ValueError("Batch does not exist")
        
        current_time = len(self.state_batches)
        batch = self.state_batches[batch_index]
        if current_time - batch["timestamp"] > self.challenge_window:
            raise ValueError("Challenge window closed")

        if "invalid" in proof_data:
            self.challenges[batch_index] = True
            self.state_batches = self.state_batches[:batch_index]
            return True
        return False

    def withdraw(self, withdrawal_id: str, user: str, amount: int, batch_index: int) -> bool:
        """
        Claims L2 assets back on L1 after the challenge window expires.
        """
        if batch_index >= len(self.state_batches):
            raise ValueError("State root not yet finalized")
        
        if self.challenges.get(batch_index, False):
            raise ValueError("Batch was invalidated by fraud proof")

        batch = self.state_batches[batch_index]
        current_time = len(self.state_batches)
        if current_time - batch["timestamp"] <= self.challenge_window:
            raise ValueError("Challenge window is still open")

        self.withdrawals[withdrawal_id] = {"user": user, "amount": amount, "finalized": True}
        return True
