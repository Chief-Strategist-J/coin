from typing import Dict, Any, Tuple

class DexMarketMaker:
    """
    Decentralized Exchange (DEX) Automated Market Maker (AMM) logic.
    Executes trustlessly on top of the L1 Execution State Machine.
    Utilizes constant product formula (x * y = k) for token swaps.
    """
    def __init__(self, token_a: str, token_b: str):
        self.token_a = token_a
        self.token_b = token_b
        self.reserve_a = 0
        self.reserve_b = 0
        self.liquidity_providers: Dict[str, int] = {}
        self.total_shares = 0

    def add_liquidity(self, provider: str, amount_a: int, amount_b: int) -> Tuple[int, str]:
        """
        Locks liquidity reserves and returns issued pool shares.
        """
        if amount_a <= 0 or amount_b <= 0:
            return 0, "Invalid liquidity amounts"

        if self.total_shares == 0:
            shares = amount_a  # Simple base share allocation
        else:
            # Enforce constant product ratios
            shares = min((amount_a * self.total_shares) // self.reserve_a,
                         (amount_b * self.total_shares) // self.reserve_b)

        if shares <= 0:
            return 0, "Liquidity addition provides zero shares"

        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.total_shares += shares
        self.liquidity_providers[provider] = self.liquidity_providers.get(provider, 0) + shares

        return shares, "Success"

    def swap_a_for_b(self, sender: str, amount_in: int) -> Tuple[int, str]:
        """
        Swaps Token A for Token B using Constant Product AMM formula (x * y = k).
        """
        if amount_in <= 0:
            return 0, "Invalid input amount"
        if self.reserve_a == 0 or self.reserve_b == 0:
            return 0, "Zero pool liquidity reserves"

        # Formula: (reserve_a * reserve_b) = (reserve_a + amount_in) * (reserve_b - amount_out)
        # amount_out = (reserve_b * amount_in) / (reserve_a + amount_in)
        # Applying a 0.3% fee: amount_in_with_fee = amount_in * 997
        amount_in_with_fee = amount_in * 997
        numerator = amount_in_with_fee * self.reserve_b
        denominator = (self.reserve_a * 1000) + amount_in_with_fee
        amount_out = numerator // denominator

        if amount_out <= 0:
            return 0, "Swap output too small"
        if amount_out >= self.reserve_b:
            return 0, "Insufficient pool reserve balance"

        self.reserve_a += amount_in
        self.reserve_b -= amount_out

        return amount_out, "Success"
