from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect,status
from sqlalchemy.orm import Query, Session
from database import get_db
from models.users import User
from schemas.user_schema import UserRegister, Userout,LoginResponse
from typing import Dict
from websocket_manager import manager
from datetime import datetime
import json
r=APIRouter()

@r.post('/createUser',response_model=Userout)
def createUser(u:UserRegister,db:Session=Depends(get_db)):

    d_user=db.query(User).filter(User.email==u.email).first()
    if d_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="user already register")
    n_user = User(
        username=u.username,
        email=u.email,
        
    )
    db.add(n_user)
    db.commit()
    db.refresh(n_user)
    return n_user



@r.get("/users",response_model=list[Userout])
def get_users(db:Session=Depends(get_db)):
   
    
    users = db.query(User).all()
    db.close()
    return users


# @r.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await manager.connect(websocket)
#     await manager.broadcast({
#         "type": "joined",
#         "user_id": client_id,
        
#         "message": f"{client_id} joined the chat",
#         "timestamp": datetime.now()
#     })
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_personal_message(f"You wrote: {data}", client_id)
#             await manager.broadcast(f"Client #{client_id} says: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client #{client_id} left the chat")



connections = {}

@r.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
   
    # Connect user (manager handles storage)
    await manager.connect(websocket, client_id)
    
    
    await manager.send_personal_message({
        "type": "welcome",
        "client_id": client_id,
        "message": f"Client #{client_id} connected!",
        "active_users": manager.get_active_users()
    }, client_id)
    
    # Notify others
    await manager.broadcast({
        "type": "user_joined",
        "client_id": client_id,
        "message": f"Client #{client_id} joined",
        "active_users": manager.get_active_users()
    }, exclude_id=client_id)
    
    # Listen for messages
    try:
        while True:
            data = await websocket.receive_text()
            
            msg_data = json.loads(data)
            target_id = msg_data.get("to")  # {"to": 2, "content": "hey"}
            if target_id:
                    await manager.send_to_client({
                        "type": "private_message",
                        "from": client_id,
                        "content": msg_data.get("content"),
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }, target_id)
            else:
                    await manager.broadcast({
                "type": "message",
                "from": client_id,
                "content": data,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
    
    except WebSocketDisconnect:
        # Disconnect user (manager handles cleanup)
        manager.disconnect(client_id)
        
        # Notify others
        await manager.broadcast({
            "type": "user_left",
            "client_id": client_id,
            "message": f"Client #{client_id} left",
            "active_users": manager.get_active_users()
        })
