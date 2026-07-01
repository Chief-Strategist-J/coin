import enum
from typing import Dict, Set, List, Optional
import uuid
import time

class NodeType(enum.Enum):
    VALIDATOR = "validator"
    FULL = "full"
    ARCHIVE = "archive"
    LIGHT = "light"
    RPC = "rpc"

class Peer:
    def __init__(self, peer_id: str, node_type: NodeType, address: str):
        self.peer_id = peer_id
        self.node_type = node_type
        self.address = address
        self.reputation: int = 100
        self.last_seen: float = time.time()
        self.connected: bool = False

    def update_reputation(self, delta: int):
        self.reputation = max(0, min(100, self.reputation + delta))

    def update_seen(self):
        self.last_seen = time.time()

class P2PNodeInterface:
    """
    Core P2P Node Interface that all Node classes must implement.
    """
    def __init__(self, node_id: str, node_type: NodeType, listen_address: str):
        self.node_id = node_id or str(uuid.uuid4())
        self.node_type = node_type
        self.listen_address = listen_address
        self.peers: Dict[str, Peer] = {}
        self.topics: Dict[str, Set[str]] = {}  
        self.is_running: bool = False

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False

    def add_peer(self, peer: Peer) -> bool:
        if peer.peer_id == self.node_id:
            return False
        self.peers[peer.peer_id] = peer
        peer.connected = True
        return True

    def remove_peer(self, peer_id: str) -> bool:
        if peer_id in self.peers:
            self.peers[peer_id].connected = False
            del self.peers[peer_id]
            for topic in self.topics:
                self.topics[topic].discard(peer_id)
            return True
        return False

    def subscribe(self, topic: str, peer_id: str) -> None:
        if peer_id not in self.peers:
            raise ValueError(f"Peer {peer_id} not connected")
        if topic not in self.topics:
            self.topics[topic] = set()
        self.topics[topic].add(peer_id)

    def unsubscribe(self, topic: str, peer_id: str) -> None:
        if topic in self.topics:
            self.topics[topic].discard(peer_id)

    def publish(self, topic: str, message: bytes) -> List[str]:
        """
        Gossip broadcast pattern: send message to all peers subscribed to the topic.
        Returns a list of peer_ids that the message was sent to.
        """
        if not self.is_running:
            raise RuntimeError("Node is not running")
        
        sent_to = []
        if topic in self.topics:
            for peer_id in self.topics[topic]:
                peer = self.peers.get(peer_id)
                if peer and peer.connected and peer.reputation > 20:  
                    sent_to.append(peer_id)
        return sent_to
