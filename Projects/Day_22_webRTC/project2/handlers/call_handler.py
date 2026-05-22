from database.connection import SessionLocal
from models.call_log import CallLog, CallStatus
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from utils.websocket_manager import manager

async def handle_call_initiated(caller_id: int, caller_username: str, receiver_id: int, call_type: str, db: Session):
    """Log call initiation and notify receiver"""
    # Create call log entry
    call_log = CallLog(
        caller_id=caller_id,
        receiver_id=receiver_id,
        call_type=call_type,
        status="initiated"
    )
    db.add(call_log)
    db.commit()
    
    # Check if receiver is online
    if manager.is_user_online(receiver_id):
        await manager.send_call_signal(caller_id, receiver_id, {
            "action": "incoming_call",
            "call_type": call_type,
            "caller_username": caller_username,
            "call_id": call_log.id
        })
    
    return call_log.id

async def handle_call_answered(call_id: int, db: Session):
    """Update call status to answered"""
    call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
    if call_log:
        call_log.status = "answered"
        call_log.started_at = datetime.now(timezone.utc)
        db.commit()

async def handle_call_ended(call_id: int, db: Session):
    """End call and calculate duration"""
    call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
    if call_log and call_log.started_at:
        call_log.status = "ended"
        call_log.ended_at = datetime.now(timezone.utc)
        duration = (call_log.ended_at - call_log.started_at).total_seconds()
        call_log.duration_seconds = int(duration)
        db.commit()

async def handle_call_rejected(call_id: int, db: Session):
    """Mark call as rejected"""
    call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
    if call_log:
        call_log.status = "rejected"
        db.commit()

async def handle_call_missed(call_id: int, db: Session):
    """Mark call as missed"""
    call_log = db.query(CallLog).filter(CallLog.id == call_id).first()
    if call_log:
        call_log.status = "missed"
        db.commit()