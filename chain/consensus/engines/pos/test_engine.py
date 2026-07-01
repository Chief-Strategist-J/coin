import unittest
from chain.consensus.engines.pos.engine import ProofOfStakeEngine
from chain.consensus.interface.engine import Block

class TestPoSEngine(unittest.TestCase):
    def setUp(self):
        self.initial_stakes = {
            "val-1": 2000,
            "val-2": 1500,
            "val-3": 1500,
            "val-4": 1000
        }
        self.engine = ProofOfStakeEngine(self.initial_stakes, minimum_stake=1000)

    def test_propose_block_sufficient_stake(self):
        txs = [{"txid": "1", "amount": 50}]
        block = self.engine.propose_block("val-1", txs, "parent")
        self.assertEqual(block.validator, "val-1")
        self.assertIn("sig-val-1", block.signatures)

    def test_propose_block_insufficient_stake(self):
        self.engine.update_validator_set({"stake_add": ("low-val", 500)})
        txs = [{"txid": "1", "amount": 50}]
        with self.assertRaises(ValueError):
            self.engine.propose_block("low-val", txs, "parent")

    def test_equivocation_slashing(self):
        self.engine.register_signature(10, "val-1", "hash-A")
        
        with self.assertRaises(ValueError) as context:
            self.engine.register_signature(10, "val-1", "hash-B")
        self.assertIn("Equivocation detected", str(context.exception))
        self.assertIn("val-1", self.engine.slashed_validators)
        self.assertEqual(self.engine.stakes["val-1"], 0)

    def test_finalize_block_stake_weight(self):
        txs = []
        block = self.engine.propose_block("val-1", txs, "parent")
        
        with self.assertRaises(ValueError) as context:
            self.engine.finalize_block(block)
        self.assertIn("Insufficient stake weight", str(context.exception))

        block.signatures.append("sig-val-2")
        block.signatures.append("sig-val-3")

        finalized = self.engine.finalize_block(block)
        self.assertEqual(finalized.consensus_proof["signed_stake"], 5000)

    def test_weak_subjectivity_checkpoint(self):
        self.engine.add_checkpoint(1, "checkpoint_hash_1")
        self.assertEqual(self.engine.checkpoints[1], "checkpoint_hash_1")

if __name__ == '__main__':
    unittest.main()
