import unittest
from chain.contracts.core.dex import DexMarketMaker

class TestDexCore(unittest.TestCase):
    def setUp(self):
        # Initialize DEX with Token A (e.g. USDT) and Token B (e.g. COIN)
        self.dex = DexMarketMaker("USDT", "COIN")

    def test_add_liquidity(self):
        shares, msg = self.dex.add_liquidity("alice", 10000, 10000)
        self.assertEqual(msg, "Success")
        self.assertEqual(shares, 10000)
        self.assertEqual(self.dex.reserve_a, 10000)
        self.assertEqual(self.dex.reserve_b, 10000)
        self.assertEqual(self.dex.total_shares, 10000)

    def test_swap_constant_product(self):
        # Alice bootstraps liquidity with 10,000 USDT and 10,000 COIN
        self.dex.add_liquidity("alice", 10000, 10000)
        
        # Bob swaps 1,000 USDT (Token A) to get COIN (Token B)
        # Using constant product formula: (reserve_b * (amount_in * 0.997)) / (reserve_a + (amount_in * 0.997))
        # numerator = 10000 * 997 * 1000 = 9,970,000
        # denominator = (10000 * 1000) + (1000 * 997) = 10,000,000 + 997,000 = 10,997,000
        # expected_out = 9,970,000 // 10,997,000 = 906 COIN
        amount_out, msg = self.dex.swap_a_for_b("bob", 1000)
        
        self.assertEqual(msg, "Success")
        self.assertEqual(amount_out, 906)
        self.assertEqual(self.dex.reserve_a, 11000)
        self.assertEqual(self.dex.reserve_b, 9094) # 10000 - 906 = 9094

if __name__ == '__main__':
    unittest.main()
