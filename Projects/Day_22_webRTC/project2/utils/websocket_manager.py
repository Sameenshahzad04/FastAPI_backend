from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict,Set
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_call_sessions: Dict[int, Set[int]] = {}  # Track active call sessions
    
    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # Clean up call sessions
        if client_id in self.user_call_sessions:
            del self.user_call_sessions[client_id]

    async def send_personal_message(self, message: dict, client_id: int):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: dict, exclude_id: int = None):
        message_json = json.dumps(message)
        for cid, conn in self.active_connections.items():
            if exclude_id is None or cid != exclude_id:
                await conn.send_text(message_json)
    
    async def send_to_client(self, message: dict, client_id: int):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))
    
    def get_active_users(self):
        return list(self.active_connections.keys())
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections
    
    async def send_call_signal(self, caller_id: int, receiver_id: int, signal_data: dict):
        """Send WebRTC signaling data to receiver"""
        print(f" Sending call signal from {caller_id} to {receiver_id}")
        print(f"Active connections: {list(self.active_connections.keys())}")
        
        if receiver_id in self.active_connections:
            message = {
                "type": "webrtc_signal",
                "caller_id": caller_id,
                "signal": signal_data
            }
            await self.send_personal_message(message, receiver_id)
            print(f"**** Call signal sent to {receiver_id}")
        else:
            print(f"**** Receiver {receiver_id} is OFFLINE or not connected!")
    
    async def send_call_response(self, receiver_id: int, caller_id: int, response: dict):
        """Send call response back to caller"""
        if caller_id in self.active_connections:
            message = {
                "type": "call_response",
                "receiver_id": receiver_id,
                "response": response
            }
            await self.send_personal_message(message, caller_id)
    def get_active_users(self):
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections



manager = ConnectionManager()