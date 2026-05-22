#why need websocket
#because in HTTP protocol after every request get respnse , the connection will be closed, 
# so if u want to make another request, u need to establish a new connection, which is not efficient
#  and also not suitable for real-time communication,
# so if we want to send message to client, we need to use websocket, which can keep the connection alive 
# and allow us to send message to client at any time. 

#jinjaTemplate is a template engine for python, it can be used to render html templates,


from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from typing import List, Dict
from jose import jwt
from config.config import SECRET_KEY, ALGORITHM

websocket_router = APIRouter()

#we get request continuously from client,so we continouly accept websocket connection
# self.active_connections: Dict[int, List[WebSocket]] = {}  # org_id -> list of connections {1:[org1_user1, org1_user2]}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.user_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()  #for accpeting the websocket connection
        org_id = user.org_id or 0
        if org_id not in self.active_connections:
            self.active_connections[org_id] = []
        self.active_connections[org_id].append(websocket)
        self.user_connections[user.id] = websocket
    
    def disconnect(self, websocket: WebSocket, user: User):
        org_id = user.org_id or 0
        if org_id in self.active_connections:
            self.active_connections[org_id].remove(websocket)
        if user.id in self.user_connections:
            del self.user_connections[user.id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_json(message)
    
    async def broadcast_to_org(self, message: dict, org_id: int):
        if org_id in self.active_connections:
            for connection in self.active_connections[org_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@websocket_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        
        if not user_id:
            await websocket.close(code=4000)
            return
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4001)
            return
        
        await manager.connect(websocket, user)
        await websocket.send_json({
            "type": "connected",
            "user_id": user.id,
            "org_id": user.org_id
        })
        
        try:
            while True:
                data = await websocket.receive_json()
                # You can process messages here if needed
        except WebSocketDisconnect:
            manager.disconnect(websocket, user)
    
    except Exception as e:
        await websocket.close(code=4002)