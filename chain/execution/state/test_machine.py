import unittest
import hashlib
from chain.vm.evm.engine import DummyEVM
from chain.execution.state.machine import StateMachine, Account

class TestL1StateMachineAndVM(unittest.TestCase):
    def setUp(self):
        self.vm = DummyEVM()
        self.state_machine = StateMachine(self.vm)
        
        acc1 = self.state_machine.get_or_create_account("alice")
        acc1.balance = 50000
        
        acc2 = self.state_machine.get_or_create_account("bob")
        acc2.balance = 1000

    def test_deterministic_state_root(self):
        root1 = self.state_machine.compute_state_root()
        root2 = self.state_machine.compute_state_root()
        self.assertEqual(root1, root2)

        self.state_machine.contract_storage["bob"] = {"y": 2, "x": 1}
        root3 = self.state_machine.compute_state_root()
        
        self.state_machine.contract_storage["bob"] = {"x": 1, "y": 2}
        root4 = self.state_machine.compute_state_root()
        self.assertEqual(root3, root4)

    def test_simple_transfer_transaction(self):
        tx = {
            "from": "alice",
            "to": "bob",
            "value": 1000,
            "nonce": 0,
            "gas_limit": 500,
            "bytecode": b"",
            "input": b""
        }
        success, msg = self.state_machine.process_transaction(tx)
        self.assertTrue(success)
        self.assertEqual(self.state_machine.accounts["alice"].balance, 48900)
        self.assertEqual(self.state_machine.accounts["bob"].balance, 2000)
        self.assertEqual(self.state_machine.accounts["alice"].nonce, 1)

    def test_contract_deployment_and_execution_sstoresload(self):
        tx_deploy = {
            "from": "alice",
            "to": "contract-1",
            "value": 0,
            "nonce": 0,
            "gas_limit": 6000,
            "bytecode": b"\x01" + (42).to_bytes(32, byteorder="big"),
            "input": b"storage-key-1"
        }
        success, msg = self.state_machine.process_transaction(tx_deploy)
        self.assertTrue(success, msg)
        
        contract_storage = self.state_machine.contract_storage["contract-1"]
        key = hashlib.sha256(b"storage-key-1").hexdigest()
        self.assertEqual(contract_storage[key], 42)

    def test_contract_out_of_gas_revert(self):
        tx_deploy = {
            "from": "alice",
            "to": "contract-1",
            "value": 100,
            "nonce": 0,
            "gas_limit": 100,  
            "bytecode": b"\x01" + (99).to_bytes(32, byteorder="big"),
            "input": b"key"
        }
        success, msg = self.state_machine.process_transaction(tx_deploy)
        self.assertFalse(success)
        self.assertIn("Out of Gas", msg)
        
        self.assertEqual(self.state_machine.accounts["alice"].balance, 49900) 

if __name__ == '__main__':
    unittest.main()
