import unittest
import time
from chain.p2p.transport.node import P2PNodeInterface, NodeType, Peer

class TestP2PNode(unittest.TestCase):
    def setUp(self):
        self.node_id = "node-1"
        self.node = P2PNodeInterface(self.node_id, NodeType.VALIDATOR, "127.0.0.1:4001")

    def test_initial_state(self):
        self.assertEqual(self.node.node_id, "node-1")
        self.assertEqual(self.node.node_type, NodeType.VALIDATOR)
        self.assertFalse(self.node.is_running)
        self.assertEqual(len(self.node.peers), 0)

    def test_start_stop(self):
        self.node.start()
        self.assertTrue(self.node.is_running)
        self.node.stop()
        self.assertFalse(self.node.is_running)

    def test_add_remove_peer(self):
        peer = Peer("peer-2", NodeType.FULL, "127.0.0.1:4002")
        added = self.node.add_peer(peer)
        self.assertTrue(added)
        self.assertIn("peer-2", self.node.peers)
        self.assertTrue(self.node.peers["peer-2"].connected)

        self_peer = Peer(self.node_id, NodeType.VALIDATOR, "127.0.0.1:4001")
        added_self = self.node.add_peer(self_peer)
        self.assertFalse(added_self)

        removed = self.node.remove_peer("peer-2")
        self.assertTrue(removed)
        self.assertNotIn("peer-2", self.node.peers)

    def test_subscribe_unsubscribe(self):
        peer = Peer("peer-2", NodeType.FULL, "127.0.0.1:4002")
        self.node.add_peer(peer)

        self.node.subscribe("blocks", "peer-2")
        self.assertIn("peer-2", self.node.topics["blocks"])

        self.node.unsubscribe("blocks", "peer-2")
        self.assertNotIn("peer-2", self.node.topics["blocks"])

    def test_publish_not_running(self):
        with self.assertRaises(RuntimeError):
            self.node.publish("blocks", b"test")

    def test_publish_success(self):
        self.node.start()
        peer = Peer("peer-2", NodeType.FULL, "127.0.0.1:4002")
        self.node.add_peer(peer)
        self.node.subscribe("blocks", "peer-2")

        sent_to = self.node.publish("blocks", b"test")
        self.assertEqual(sent_to, ["peer-2"])

    def test_publish_filtered_by_reputation(self):
        self.node.start()
        peer = Peer("peer-2", NodeType.FULL, "127.0.0.1:4002")
        peer.reputation = 10
        self.node.add_peer(peer)
        self.node.subscribe("blocks", "peer-2")

        sent_to = self.node.publish("blocks", b"test")
        self.assertEqual(sent_to, [])

if __name__ == '__main__':
    unittest.main()
