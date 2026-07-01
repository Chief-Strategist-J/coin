import unittest
import json
from chain.vm.evm.engine import DummyEVM
from chain.execution.state.machine import StateMachine
from chain.rpc.api.acp_adapter import ACPAdapter

class TestACPAdapter(unittest.TestCase):
    def setUp(self):
        self.vm = DummyEVM()
        self.state_machine = StateMachine(self.vm)
        self.state_machine.get_or_create_account("alice").balance = 50000
        self.adapter = ACPAdapter(self.state_machine)

    def test_process_valid_transaction_request(self):
        envelope = {
            "id": "msg-123",
            "conversation_id": "conv-456",
            "sender": "agent-uri://alice-agent",
            "receiver": "agent-uri://chain-api",
            "performative": "REQUEST",
            "content": {
                "parameters": {
                    "from": "alice",
                    "to": "bob",
                    "value": 1000,
                    "nonce": 0,
                    "gas_limit": 500
                }
            },
            "ontology": "urn:llm-observability:perplexity:v1",
            "protocol": "request-response",
            "timestamp": "2026-07-01T12:00:00Z",
            "metadata": {
                "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
            }
        }
        
        res_json = self.adapter.process_envelope(json.dumps(envelope))
        res = json.loads(res_json)
        
        self.assertEqual(res["performative"], "INFORM")
        self.assertEqual(res["content"]["parameters"]["status"], "success")
        self.assertEqual(self.state_machine.accounts["bob"].balance, 1000)

    def test_process_invalid_parameters_failure(self):
        # Missing sender / conversation_id
        envelope = {
            "id": "msg-123",
            "performative": "REQUEST",
            "content": {}
        }
        
        res_json = self.adapter.process_envelope(json.dumps(envelope))
        res = json.loads(res_json)
        
        self.assertEqual(res["performative"], "FAILURE")
        self.assertEqual(res["content"]["parameters"]["code"], -32602)

if __name__ == '__main__':
    unittest.main()
