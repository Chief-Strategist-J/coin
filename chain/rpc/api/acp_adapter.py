import json
import uuid
import time
from typing import Dict, Any, Tuple

class ACPAdapter:
    """
    Driving Adapter for Agent Communication Protocol (ACP).
    Acts strictly as an external API boundary mapping incoming envelopes 
    to underlying blockchain execution logic. Contains zero domain logic.
    """
    def __init__(self, state_machine):
        self.state_machine = state_machine

    def process_envelope(self, envelope_json: str) -> str:
        """
        Receives and processes ACP Envelope.
        Returns serialized response envelope.
        """
        try:
            msg = json.loads(envelope_json)
        except json.JSONDecodeError:
            return self._build_failure_envelope(None, None, -32700, "Parse Error")

        conv_id = msg.get("conversation_id")
        sender = msg.get("sender")
        msg_id = msg.get("id")

        # 1. Validation
        if not conv_id or not sender:
            return self._build_failure_envelope(conv_id, msg_id, -32602, "Invalid Params: missing conversation_id or sender")

        performative = msg.get("performative")
        if performative != "REQUEST":
            return self._build_failure_envelope(conv_id, msg_id, -32600, f"Unsupported Performative: {performative}")

        # 2. Extract transaction payload
        content = msg.get("content", {})
        tx = content.get("parameters")
        if not tx:
            return self._build_failure_envelope(conv_id, msg_id, -32602, "Missing transaction parameters")

        # Map to State Machine Core Service Layer (Hexagonal Driving Pattern)
        try:
            # Enforce binary formatting for inputs in State Machine
            tx_payload = {
                "from": tx["from"],
                "to": tx["to"],
                "value": tx["value"],
                "nonce": tx["nonce"],
                "gas_limit": tx.get("gas_limit", 1000),
                "bytecode": tx.get("bytecode", "").encode() if isinstance(tx.get("bytecode"), str) else tx.get("bytecode", b""),
                "input": tx.get("input", "").encode() if isinstance(tx.get("input"), str) else tx.get("input", b"")
            }
            success, detail = self.state_machine.process_transaction(tx_payload)
            if not success:
                return self._build_failure_envelope(conv_id, msg_id, -32603, f"Execution Reverted: {detail}")
            
            # 3. Respond with SUCCESS (INFORM Performative)
            state_root = self.state_machine.compute_state_root()
            return json.dumps({
                "id": str(uuid.uuid4()),
                "conversation_id": conv_id,
                "sender": "agent-uri://chain-api",
                "receiver": sender,
                "performative": "INFORM",
                "content": {
                    "response_text": "Transaction executed successfully",
                    "parameters": {
                        "status": "success",
                        "block_height": self.state_machine.block_height,
                        "state_root": state_root
                    }
                },
                "ontology": "urn:llm-observability:perplexity:v1",
                "protocol": "request-response",
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "metadata": {
                    "traceparent": msg.get("metadata", {}).get("traceparent", "")
                }
            })

        except Exception as e:
            return self._build_failure_envelope(conv_id, msg_id, -32603, f"Internal Error: {str(e)}")

    def _build_failure_envelope(self, conv_id: str, receiver: str, code: int, message: str) -> str:
        return json.dumps({
            "id": str(uuid.uuid4()),
            "conversation_id": conv_id or str(uuid.uuid4()),
            "sender": "agent-uri://chain-api",
            "receiver": receiver or "unknown",
            "performative": "FAILURE",
            "content": {
                "response_text": message,
                "parameters": {
                    "code": code,
                    "error_message": message
                }
            },
            "ontology": "urn:llm-observability:perplexity:v1",
            "protocol": "request-response",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "metadata": {}
        })
