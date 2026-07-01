import hashlib
from typing import Dict, Any, Tuple
from chain.vm.interface.vm import VMInterface

class DummyEVM(VMInterface):
    """
    EVM compatible sandboxed execution engine following VMInterface.
    Performs deterministic calculations, gas metering, state updates, and error handling.
    """
    def execute(self, bytecode: bytes, input_data: bytes, state: Dict[str, Any], gas_limit: int) -> Tuple[bytes, Dict[str, Any], int, Any]:
        gas_used = 0
        new_state = dict(state)
        
        # 1. Base deployment/exec parsing cost
        gas_used += 100
        if gas_used > gas_limit:
            return b"", state, gas_limit, "Out of Gas"

        # Safe deterministic execution based on opcode simulation
        if not bytecode:
            return b"", new_state, gas_used, None

        # Simulate instruction operations:
        # Instruction structure: byte[0] = operation, byte[1:] = key/value mapping or math parameters
        op = bytecode[0]
        
        # Opcodes:
        # 0x01: SSTORE (Store value in state: key derived from input_data, value from rest of bytecode)
        # 0x02: SLOAD (Load value from state)
        # 0x03: ADD (Arithmetic sum: 256-bit safe integer math)
        try:
            if op == 0x01:
                gas_used += 5000  # SSTORE gas cost
                if gas_used > gas_limit:
                    return b"", state, gas_limit, "Out of Gas"
                
                key = hashlib.sha256(input_data).hexdigest()
                val = int.from_bytes(bytecode[1:], byteorder="big")
                new_state[key] = val
                return val.to_bytes(32, byteorder="big"), new_state, gas_used, None
                
            elif op == 0x02:
                gas_used += 200  # SLOAD gas cost
                if gas_used > gas_limit:
                    return b"", state, gas_limit, "Out of Gas"
                
                key = hashlib.sha256(input_data).hexdigest()
                val = new_state.get(key, 0)
                return val.to_bytes(32, byteorder="big"), new_state, gas_used, None
                
            elif op == 0x03:
                gas_used += 10  # ADD gas cost
                if gas_used > gas_limit:
                    return b"", state, gas_limit, "Out of Gas"
                
                val1 = int.from_bytes(input_data, byteorder="big")
                val2 = int.from_bytes(bytecode[1:], byteorder="big")
                # Secure integer 256-bit wrap subtraction/addition
                res = (val1 + val2) & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
                return res.to_bytes(32, byteorder="big"), new_state, gas_used, None
                
            else:
                return b"", state, gas_used, "Unknown Opcode"
        except Exception as e:
            return b"", state, gas_used, f"VM Execution Error: {str(e)}"

    def validate(self, bytecode: bytes) -> bool:
        if len(bytecode) == 0:
            return False
        # Valid opcodes must be within our supported simulated byte list
        return bytecode[0] in [0x01, 0x02, 0x03]

    def estimate_gas(self, bytecode: bytes, input_data: bytes) -> int:
        if not bytecode:
            return 100
        op = bytecode[0]
        if op == 0x01:
            return 100 + 5000
        elif op == 0x02:
            return 100 + 200
        elif op == 0x03:
            return 100 + 10
        return 100
