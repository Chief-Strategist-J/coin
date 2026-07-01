import unittest
import time
from chain.consensus.engines.poa.engine import ProofOfAuthorityEngine
from chain.consensus.interface.engine import Block

class TestPoAEngine(unittest.TestCase):
    def setUp(self):
        self.validators = ["val-1", "val-2", "val-3", "val-4"]
        self.engine = ProofOfAuthorityEngine(self.validators)

    def test_propose_block_authorized(self):
        txs = [{"txid": "1", "amount": 100}]
        block = self.engine.propose_block("val-1", txs, "genesis_hash")
        self.assertEqual(block.validator, "val-1")
        self.assertEqual(block.parent_hash, "genesis_hash")
        self.assertEqual(block.transactions, txs)
        self.assertEqual(block.signatures, ["sig-val-1"])

    def test_propose_block_unauthorized(self):
        txs = [{"txid": "1", "amount": 100}]
        with self.assertRaises(ValueError):
            self.engine.propose_block("rogue-val", txs, "genesis_hash")

    def test_validate_block(self):
        txs = [{"txid": "1", "amount": 100}]
        block = self.engine.propose_block("val-1", txs, "genesis_hash")
        
        self.assertTrue(self.engine.validate_block(block))

        block.transactions = [{"txid": "1", "amount": 200}]
        self.assertFalse(self.engine.validate_block(block))

    def test_finalize_block_insufficient_signatures(self):
        txs = [{"txid": "1", "amount": 100}]
        block = self.engine.propose_block("val-1", txs, "genesis_hash")
        
        with self.assertRaises(ValueError) as context:
            self.engine.finalize_block(block)
        self.assertIn("Insufficient signatures", str(context.exception))

    def test_finalize_block_success(self):
        txs = [{"txid": "1", "amount": 100}]
        block = self.engine.propose_block("val-1", txs, "genesis_hash")
        
        block.signatures.append("sig-val-2")
        block.signatures.append("sig-val-3")

        finalized = self.engine.finalize_block(block)
        self.assertEqual(finalized.block.block_hash, block.block_hash)
        self.assertEqual(finalized.consensus_proof["consensus"], "PoA")
        self.assertEqual(len(finalized.consensus_proof["signatures"]), 3)

    def test_update_validator_set(self):
        self.engine.update_validator_set({"add": "val-5"})
        self.assertIn("val-5", self.engine.get_validator_set())

        self.engine.update_validator_set({"remove": "val-5"})
        self.assertNotIn("val-5", self.engine.get_validator_set())

        with self.assertRaises(ValueError):
            self.engine.update_validator_set({"remove": "val-4"})

if __name__ == '__main__':
    unittest.main()
