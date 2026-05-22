
from fastapi import WebSocket

from database import SessionLocal
from models.user import User
from jwt import verify_websocket_token
from config.config import SECRET_KEY, ALGORITHM
from typing import Dict, List
# import asyncio

#  ConnectionManager tracks who is connected via WebSocket.
# Without this, server wouldn't know where to send notifications.
# We store connections by org_id (for team broadcasts) and by
# user_id (for private messages). 


class ConnectionManager:
    def __init__(self):
        # to store connections in  grouped by organization: {org_id: [ws1, ws2]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
        #  to store connections by user ID: {user_id: websocket}
       
        self.user_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user: User):
        # This method accepts the WebSocket handshake and registers connection.
        # When a client connects we first accept the connection (with upgrades
        # from HTTP to WebSocket protocol), then we store the connection in
        # both dictionaries so we can find it later for sending messages.
     
        await websocket.accept()
        if user.role_name == "super_admin":
            org_id = 0
        else:
            org_id = user.org_id 
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        self.user_connections[user.id] = websocket
    
    def disconnect(self, websocket: WebSocket, user: User):
        # This method cleans up when a user disconnects. We remove their
        # connection from both dictionaries so we don't try to send
        # messages to a closed connection (which would cause errors).
        if user.role_name == "super_admin":
            org_id = 0
        else:
            org_id = user.org_id
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
        if user.id in self.user_connections:
            del self.user_connections[user.id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        # This sends a message to ONE specific user (like a private DM).
        # We look up their WebSocket connection by user_id and send JSON.
       if user_id in self.user_connections:
            await self.user_connections[user_id].send_json(message)
    
    async def broadcast_to_org(self, message: dict, org_id: int):
        # Send to ALL users in organization (team announcement)

        if org_id in self.active_connections:
            for connection in self.active_connections[org_id]:
                await connection.send_json(message)

#  created ONE global manager that all routes will use.

ws_manager = ConnectionManager()

#  When a client wants to connect via WebSocket, they connect to /ws with their JWT token.
# This function validates the token, finds the user, and registers


async def websocket_endpoint(websocket: WebSocket):
    # The client connects with a token like: ws://localhost:8000/ws?token=eyJhbG...
    # We extract the token from the query parameters (the part after ?)
    
    token = websocket.query_params.get("token")
    
    if not token:
        # No token means we can't authenticate, so we close the connection
        # with error code 4000 (custom code meaning "missing token")
        await websocket.close(code=4000)
        raise Exception("WebSocket connection rejected: No token provided")
    
    
        # Decode and validate the JWT token using verify_websocket_token function. This checks the token's signature,
        # expiration, and retrieves the user from the database. If token is invalid or user not found, it raises an exception.
    db=SessionLocal()
    user = verify_websocket_token(token, db)
        
    if not user:
       
                  await websocket.close(code=4000)
                  db.close()
                  raise Exception("WebSocket connection rejected: Invalid token")
        
        
       
        # Register connection
    await ws_manager.connect(websocket, user)
    
          # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "user_id": user.id,
        "org_id": user.org_id
    })
        
        # This infinite loop keeps the connection alive and listens for
        # any messages from the client. The loop runs forever until the
        # client disconnects (which raises WebSocketDisconnect exception).
       
    try:
            while True:
                # Wait for message from client (blocks until message arrives)
                data = await websocket.receive_json()
                  # Acknowledge receipt like i get the msg
                # - Mark notification as read
                # - Send chat messages to teammates
                await websocket.send_json({
                    "type": "ack",
                    "data": data
                })
        
    except Exception:
            # Client disconnected - clean up their connection
            ws_manager.disconnect(websocket, user)
    
    finally:
            db.close()