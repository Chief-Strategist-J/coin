import unittest
from chain.contracts.core.dex import DexMarketMaker

class TestDexCore(unittest.TestCase):
    def setUp(self):
        self.dex = DexMarketMaker("USDT", "COIN")

    def test_add_liquidity(self):
        shares, msg = self.dex.add_liquidity("alice", 10000, 10000)
        self.assertEqual(msg, "Success")
        self.assertEqual(shares, 10000)
        self.assertEqual(self.dex.reserve_a, 10000)
        self.assertEqual(self.dex.reserve_b, 10000)
        self.assertEqual(self.dex.total_shares, 10000)

    def test_swap_constant_product(self):
        self.dex.add_liquidity("alice", 10000, 10000)
        
        amount_out, msg = self.dex.swap_a_for_b("bob", 1000)
        
        self.assertEqual(msg, "Success")
        self.assertEqual(amount_out, 906)
        self.assertEqual(self.dex.reserve_a, 11000)
        self.assertEqual(self.dex.reserve_b, 9094) 

if __name__ == '__main__':
    unittest.main()
