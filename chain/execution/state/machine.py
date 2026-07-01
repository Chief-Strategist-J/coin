import hashlib
from typing import Dict, Any, Tuple, List
import time

class Account:
    def __init__(self, address: str, balance: int = 0, nonce: int = 0):
        self.address = address
        self.balance = balance
        self.nonce = nonce
        self.contract_code: bytes = b""

class StateMachine:
    """
    Deterministic L1 execution state machine coordinating accounts, balances, gas fees, 
    transactions, block assembly, and State root hashes.
    """
    def __init__(self, vm_engine):
        self.vm_engine = vm_engine
        self.accounts: Dict[str, Account] = {}
        self.contract_storage: Dict[str, Dict[str, Any]] = {}
        self.block_height: int = 0

    def get_or_create_account(self, address: str) -> Account:
        if address not in self.accounts:
            self.accounts[address] = Account(address)
        return self.accounts[address]

    def compute_state_root(self) -> str:
        """
        Cryptographic verification root of total state. 
        Iterates and hashes state details in a sorted, deterministic order.
        """
        hash_inputs = []
        for addr in sorted(self.accounts.keys()):
            acc = self.accounts[addr]
            storage_hash = ""
            if addr in self.contract_storage:
                storage_keys = sorted(self.contract_storage[addr].keys())
                storage_hash = hashlib.sha256(str([(k, self.contract_storage[addr][k]) for k in storage_keys]).encode()).hexdigest()
            acc_data = f"{acc.address}-{acc.balance}-{acc.nonce}-{acc.contract_code.hex()}-{storage_hash}"
            hash_inputs.append(acc_data)
        
        raw_state = "|".join(hash_inputs)
        return hashlib.sha256(raw_state.encode()).hexdigest()

    def process_transaction(self, tx: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Applies a transaction to the state.
        Format: {"from": str, "to": str, "value": int, "nonce": int, "gas_limit": int, "bytecode": bytes, "input": bytes}
        """
        sender = self.get_or_create_account(tx["from"])
        recipient = self.get_or_create_account(tx["to"])

        if tx["nonce"] != sender.nonce:
            return False, "Invalid Transaction Nonce"
        
        gas_cost = tx.get("gas_limit", 1000) * 1  
        total_debit = tx["value"] + gas_cost
        
        if sender.balance < total_debit:
            return False, "Insufficient Balance"

        sender.balance -= total_debit
        sender.nonce += 1

        if tx.get("bytecode"):
            recipient.contract_code = tx["bytecode"]
            storage = self.contract_storage.get(recipient.address, {})
            
            output, new_storage, gas_used, err = self.vm_engine.execute(
                tx["bytecode"], tx.get("input", b""), storage, tx["gas_limit"]
            )
            
            if err:
                sender.balance += tx["value"]
                return False, f"Contract execution failed: {err}"
            
            self.contract_storage[recipient.address] = new_storage
            recipient.balance += tx["value"]
            refund = (tx["gas_limit"] - gas_used) * 1
            sender.balance += refund
        else:
            recipient.balance += tx["value"]
            sender.balance += (tx["gas_limit"] - 100) * 1

        return True, "Success"

    def transition_state(self, block_transactions: List[Dict[str, Any]]) -> str:
        """
        Main transition function: State(n+1) = Transition(State(n), Block(n))
        """
        for tx in block_transactions:
            self.process_transaction(tx)
        
        self.block_height += 1
        return self.compute_state_root()
