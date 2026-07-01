import unittest
from chain.l2.bridge.bridge import L1BridgeContract

class TestL2BridgeAndRollup(unittest.TestCase):
    def setUp(self):
        self.bridge = L1BridgeContract(challenge_window=3)

    def test_deposit(self):
        res = self.bridge.deposit("alice", 500)
        self.assertEqual(res["amount"], 500)
        self.assertEqual(self.bridge.deposits["alice"], 500)

    def test_submit_state_batch(self):
        self.bridge.submit_state_batch(0, "state_root_1", ["tx_1", "tx_2"], "sequencer-1")
        self.assertEqual(len(self.bridge.state_batches), 1)
        self.assertEqual(self.bridge.state_batches[0]["state_root"], "state_root_1")

    def test_challenge_fraud_proof_window(self):
        self.bridge.submit_state_batch(0, "state_root_1", ["tx_1"], "sequencer-1")
        
        challenged = self.bridge.challenge_batch(0, "invalid_tx_proof")
        self.assertTrue(challenged)
        self.assertTrue(self.bridge.challenges[0])
        self.assertEqual(len(self.bridge.state_batches), 0)  

    def test_withdraw_finalization(self):
        self.bridge.submit_state_batch(0, "state_root_1", ["tx_1"], "sequencer-1")
        self.bridge.submit_state_batch(1, "state_root_2", ["tx_2"], "sequencer-1")
        self.bridge.submit_state_batch(2, "state_root_3", ["tx_3"], "sequencer-1")
        self.bridge.submit_state_batch(3, "state_root_4", ["tx_4"], "sequencer-1")
        self.bridge.submit_state_batch(4, "state_root_5", ["tx_5"], "sequencer-1")

        success = self.bridge.withdraw("w_01", "alice", 200, 0)
        self.assertTrue(success)
        self.assertTrue(self.bridge.withdrawals["w_01"]["finalized"])

        with self.assertRaises(ValueError) as context:
            self.bridge.withdraw("w_02", "alice", 100, 4)
        self.assertIn("Challenge window is still open", str(context.exception))

if __name__ == '__main__':
    unittest.main()
