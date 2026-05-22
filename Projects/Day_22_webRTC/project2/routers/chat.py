from fastapi import APIRouter, WebSocket, Query, Depends
from utils.websocket_manager import manager
from utils.security import verify_token
from database.connection import SessionLocal,get_db
from handlers.chat_handler import handle_chat_message, handle_user_join, handle_user_leave
from handlers.call_handler import (
    handle_call_initiated, handle_call_answered, 
    handle_call_ended, handle_call_rejected, handle_call_missed
)
import json
from typing import List
from models.chat_msg import ChatMessage
from sqlalchemy.orm import Session
from handlers.chat_handler import get_chat_history, search_users,get_username_by_id
from schemas.chat_schema import MessageOut

r = APIRouter()

@r.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token for authentication")
):
    payload = verify_token(token)
    
    if not payload:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = payload.get("id")
    username = payload.get("username")
    
    await manager.connect(websocket, user_id)
    
    await manager.send_personal_message({
        "type": "connected",
        "user_id": user_id,
        "message": "Welcome to chat!"
    }, user_id)
    
    await handle_user_join(user_id, username)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse JSON (expecting {receiver_id, content})
            message_data = json.loads(data)
            msg_type = message_data.get("type", "message")

            receiver_id = message_data.get("receiver_id")
            # content = message_data.get("content")
            
            # Handle WebRTC signaling messages
            if msg_type == "webrtc_offer":
                sdp_offer = message_data.get("sdp")
                call_type = message_data.get("call_type", "audio")
                call_id = message_data.get("call_id")
                
                await manager.send_call_signal(user_id, receiver_id, {
                    "action": "offer",
                    "sdp": sdp_offer,
                    "call_type": call_type,
                    "call_id": call_id,
                    "caller_username": username
                })
                
            elif msg_type == "webrtc_answer":
                sdp_answer = message_data.get("sdp")
                call_id = message_data.get("call_id")
                
                await manager.send_call_signal(user_id, receiver_id, {
                    "action": "answer",
                    "sdp": sdp_answer,
                    "call_id": call_id
                })
                
            elif msg_type == "webrtc_ice_candidate":
                candidate = message_data.get("candidate")
                call_id = message_data.get("call_id")
                
                await manager.send_call_signal(user_id, receiver_id, {
                    "action": "ice_candidate",
                    "candidate": candidate,
                    "call_id": call_id
                })
            elif msg_type == "call_accept":
                call_id = message_data.get("call_id")
                db = SessionLocal()
                await handle_call_answered(call_id, db)
                db.close()
                
                receiver_id = message_data.get("receiver_id")
                await manager.send_call_response(user_id, receiver_id, {
                    "action": "call_accepted",
                    "call_id": call_id
                })
                
            elif msg_type == "call_reject":
                call_id = message_data.get("call_id")
                db = SessionLocal()
                await handle_call_rejected(call_id, db)
                db.close()
                
                receiver_id = message_data.get("receiver_id")
                await manager.send_call_response(user_id, receiver_id, {
                    "action": "call_rejected",
                    "call_id": call_id
                })
                
            elif msg_type == "call_end":
                call_id = message_data.get("call_id")
                db = SessionLocal()
                await handle_call_ended(call_id, db)
                db.close()
                
                receiver_id = message_data.get("receiver_id")
                await manager.send_call_signal(user_id, receiver_id, {
                    "action": "call_ended",
                    "call_id": call_id
                })
                
            # Handle regular chat messages (existing functionality)
            elif msg_type == "message" or "content" in message_data:
                
                content = message_data.get("content")
                
                if not receiver_id or not content:
                    continue
                
                db = SessionLocal()
                await handle_chat_message(user_id, username, content, receiver_id, db)
                db.close()
                
    except Exception as e:
        db = SessionLocal()
        await handle_user_leave(user_id, username)
        db.close()
        manager.disconnect(user_id)


#seacrch user
@r.get("/users/search", response_model=List[dict])
def search_users_route(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user_id: int = Query(...),
    db: Session = Depends(get_db)
):
  
    users = search_users(db, current_user_id, q)
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

@r.get("/history/{other_user_id}", response_model=List[MessageOut])
def get_chat_history_route(
    other_user_id: int,
    current_user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    
    messages = get_chat_history(db, current_user_id, other_user_id)
    
    result = []
    for msg in messages:


        result.append({
            "id": msg.id,
            "sender_name": get_username_by_id(db, msg.sender_id),
            "receiver_name": get_username_by_id(db, msg.receiver_id),
            "content": msg.content,
            "timestamp": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return result

#Get list of currently online users
@r.get("/online-users")
def get_online_users(current_user_id: int = Query(...)):
   
    online = manager.get_active_users()
    # Remove self from list
    online = [uid for uid in online if uid != current_user_id]
    return {"online_users": online}


# New: Get call history
@r.get("/calls/history/{other_user_id}", response_model=List[dict])
def get_call_history(
    other_user_id: int,
    current_user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    from models.call_log import CallLog
    calls = db.query(CallLog).filter(
        ((CallLog.caller_id == current_user_id) & (CallLog.receiver_id == other_user_id)) |
        ((CallLog.caller_id == other_user_id) & (CallLog.receiver_id == current_user_id))
    ).order_by(CallLog.started_at.desc()).limit(50).all()
    
    return [{
        "id": c.id,
        "caller_id": c.caller_id,
        "receiver_id": c.receiver_id,
        "call_type": c.call_type,
        "status": c.status,
        "started_at": c.started_at.strftime("%Y-%m-%d %H:%M:%S") if c.started_at else None,
        "duration_seconds": c.duration_seconds
    } for c in calls]