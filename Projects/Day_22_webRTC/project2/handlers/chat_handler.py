from utils.websocket_manager import manager
from datetime import datetime, timezone
from models.chat_msg import ChatMessage
from models.user import User
from database.connection import SessionLocal,get_db
from sqlalchemy.orm import Query, Session
from fastapi import Depends
import json

# async def handle_chat_message(user_id: int, username: str, message: str, target_id: int = None,db:Session=Depends(get_db)):
    # message_data = {
    #     "type": "private_message" if target_id else "message",
    #     "from_user_id": user_id,
    #     "from_username": username,
    #     "content": message,
    #     "timestamp": datetime.now().strftime("%H:%M:%S")
    # }
    # #save  private msgto db 
  
    # if target_id and db:
    #     chat_message = ChatMessage(
    #         sender_id=user_id,
    #         receiver_id=target_id,
    #         content=message,
    #         created_at=datetime.now(timezone.utc)
    #     )
    #     db.add(chat_message)
    #     db.commit()
    #     db.refresh(chat_message)
    #     message_data["message_id"] = chat_message.id


    # #send private msg to a target user else:broadcast to all users except sender
    # if target_id:
    #     # await manager.send_to_client(message_data, target_id)

    #     await manager.send_to_client({
    #     "type": "message_sent",
    #     "receiver_id": target_id,
    #     "content": message,
    #     "timestamp": message_data["timestamp"]
    # }, user_id)
        
    #     await manager.send_personal_message({
    #         "type": "message_sent",
    #     "to_user_id": target_id,
    #     "content": message,
    #     "timestamp": message_data["timestamp"]
    # }, user_id)
    # else:
    #     await manager.broadcast(message_data, exclude_id=user_id)
    
    # return message_data

async def handle_chat_message(sender_id, sender_username, content, receiver_id, db):
    from models.chat_msg import ChatMessage
    from datetime import datetime, timezone
    from utils.websocket_manager import manager
    
    # Save to database
    message = ChatMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        created_at=datetime.now(timezone.utc)
    )
    db.add(message)
    db.commit()
    db.refresh(message)  # Get the ID
    
    timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    # Send to RECEIVER
    await manager.send_personal_message({
        "type": "private_message",
        "from_user_id": sender_id,
        "from_username": sender_username,
        "content": content,
        "timestamp": timestamp
    }, receiver_id)
    
    # Send confirmation to SENDER
    await manager.send_personal_message({
        "type": "message_sent",
        "to_user_id": receiver_id,
        "content": content,
        "timestamp": timestamp
    }, sender_id)
    
    return message

async def handle_user_join(user_id: int, username: str):
    await manager.broadcast({
        "type": "user_joined",
        "user_id": user_id,
        "username": username,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }, exclude_id=user_id)

async def handle_user_leave(user_id: int, username: str):
    await manager.broadcast({
        "type": "user_left",
        "user_id": user_id,
        "username": username,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def get_chat_history(db: Session, user1_id: int, user2_id: int, limit: int = 50):
    """
    Get chat history between two users
    Returns messages from both users in order
    """
    messages = db.query(ChatMessage).filter(
        ((ChatMessage.sender_id == user1_id) & (ChatMessage.receiver_id == user2_id)) |
        ((ChatMessage.sender_id == user2_id) & (ChatMessage.receiver_id == user1_id))
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    
    return messages

#   Search for users by username
  
def search_users(db: Session, current_user_id: int, search_query: str, limit: int = 10):
   
    users = db.query(User).filter(
        User.id != current_user_id,
        User.username.ilike(f"%{search_query}%")
    ).limit(limit).all()
    
    return users

def get_username_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user.username if user else "Unknown"