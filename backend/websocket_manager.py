"""
WebSocket Manager for DMR Libertas

This module manages WebSocket connections for real-time updates to the frontend.
Handles connection management, message broadcasting, and client tracking.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from uuid import uuid4

from fastapi import WebSocket

logger = logging.getLogger(__name__)

@dataclass
class Client:
    """Represents a connected WebSocket client."""
    websocket: WebSocket
    client_id: str = field(default_factory=lambda: str(uuid4()))
    subscriptions: Set[str] = field(default_factory=set)
    
    async def send_json(self, data: Any) -> bool:
        """Send JSON data to this client."""
        try:
            if isinstance(data, (dict, list)):
                data = json.dumps(data)
            await self.websocket.send_text(data)
            return True
        except Exception as e:
            logger.error(f"Error sending to client {self.client_id}: {e}")
            return False

class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[str, Client] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket) -> str:
        """Register a new WebSocket connection."""
        client = Client(websocket=websocket)
        
        async with self._lock:
            self.active_connections[client.client_id] = client
        
        logger.info(f"New WebSocket connection: {client.client_id}")
        return client.client_id
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        client_id = None
        
        # Find the client ID for this WebSocket
        for cid, client in self.active_connections.items():
            if client.websocket == websocket:
                client_id = cid
                break
        
        if client_id:
            self.active_connections.pop(client_id, None)
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, client_id: str, message: Any) -> bool:
        """Send a message to a specific client."""
        if client_id not in self.active_connections:
            return False
            
        client = self.active_connections[client_id]
        return await client.send_json(message)
    
    async def broadcast(self, message: Any, exclude: Optional[List[str]] = None) -> None:
        """Send a message to all connected clients."""
        exclude = exclude or []
        tasks = []
        
        for client_id, client in list(self.active_connections.items()):
            if client_id not in exclude:
                tasks.append(client.send_json(message))
        
        # Run sends in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_json(self, data: Any, exclude: Optional[List[str]] = None) -> None:
        """Broadcast a JSON-serializable object to all clients."""
        await self.broadcast(json.dumps(data), exclude=exclude)
    
    async def subscribe(self, client_id: str, topic: str) -> bool:
        """Subscribe a client to a topic."""
        if client_id not in self.active_connections:
            return False
            
        client = self.active_connections[client_id]
        client.subscriptions.add(topic)
        logger.debug(f"Client {client_id} subscribed to {topic}")
        return True
    
    async def unsubscribe(self, client_id: str, topic: str) -> bool:
        """Unsubscribe a client from a topic."""
        if client_id not in self.active_connections:
            return False
            
        client = self.active_connections[client_id]
        client.subscriptions.discard(topic)
        logger.debug(f"Client {client_id} unsubscribed from {topic}")
        return True
    
    async def publish(self, topic: str, message: Any) -> None:
        """Publish a message to all clients subscribed to a topic."""
        tasks = []
        
        for client in self.active_connections.values():
            if topic in client.subscriptions:
                tasks.append(client.send_json({
                    "type": "pubsub",
                    "topic": topic,
                    "data": message
                }))
        
        # Run sends in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_client_count(self) -> int:
        """Get the number of connected clients."""
        return len(self.active_connections)
    
    def get_connected_clients(self) -> List[Dict[str, Any]]:
        """Get information about all connected clients."""
        return [
            {
                "client_id": client.client_id,
                "subscriptions": list(client.subscriptions),
                "connected_at": getattr(client.websocket, "connected_at", None)
            }
            for client in self.active_connections.values()
        ]

# Singleton instance
manager = ConnectionManager()