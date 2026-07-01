from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class VMInterface(ABC):
    """
    Modular VM Abstraction Layer interface that all VMs (EVM, WASM, Custom) must implement.
    Allows executing smart contracts in a sandboxed, deterministic manner.
    """
    
    @abstractmethod
    def execute(self, bytecode: bytes, input_data: bytes, state: Dict[str, Any], gas_limit: int) -> Tuple[bytes, Dict[str, Any], int, Any]:
        """
        Executes the given bytecode in a sandbox.
        Returns: (output, new_state, gas_used, error)
        """
        pass

    @abstractmethod
    def validate(self, bytecode: bytes) -> bool:
        """
        Validates the safety and syntax correctness of the bytecode before deployment.
        """
        pass

    @abstractmethod
    def estimate_gas(self, bytecode: bytes, input_data: bytes) -> int:
        """
        Estimates the gas consumed during contract execution.
        """
        pass
