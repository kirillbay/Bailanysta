"""WebSocket endpoint — auth via cookie, channel subscription with membership check."""

import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import COOKIE_NAME, decode_token
import app.database.session as db_session
from app.models.user import User
from app.models.club import ClubMember
from app.models.club_channel import ClubChannel
from app.realtime.manager import manager

router = APIRouter()

def _get_user_from_token(token: str, db: Session):
    try:
        payload = decode_token(token)
        uid = uuid.UUID(str(payload.get("sub")))
        if payload.get("type") != "access":
            return None
        user = db.query(User).filter(User.id == uid).first()
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Auth with short-lived session
    db_auth = db_session.SessionLocal()
    try:
        auth_token = websocket.query_params.get("token")
        if not auth_token:
            auth_token = websocket.cookies.get(COOKIE_NAME)
        if not auth_token:
            await websocket.close(code=4401)
            return
        user = _get_user_from_token(auth_token, db_auth)
        if not user:
            await websocket.close(code=4401)
            return
        user_id = str(user.id)
    finally:
        db_auth.close()

    await manager.connect(websocket, user_id)
    await websocket.send_text(json.dumps({"type": "connected", "payload": {"user_id": user_id}}))

    try:
        while True:
            try:
                data = await websocket.receive_text()
                if len(data) > 10000:
                    await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "Payload too large"}}))
                    continue
                try:
                    msg = json.loads(data)
                except Exception:
                    await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "Invalid JSON"}}))
                    continue

                mtype = msg.get("type")
                payload = msg.get("payload", {})

                if mtype == "subscribe":
                    channel_id = payload.get("channel_id")
                    if not channel_id:
                        await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "channel_id required"}}))
                        continue
                    try:
                        cid = uuid.UUID(str(channel_id))
                    except Exception:
                        await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "Invalid channel_id"}}))
                        continue
                    db_sub = db_session.SessionLocal()
                    try:
                        ch = db_sub.query(ClubChannel).filter(ClubChannel.id == cid).first()
                        if not ch:
                            await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "Channel not found"}}))
                            continue
                        is_member = db_sub.query(ClubMember).filter(ClubMember.club_id == ch.club_id, ClubMember.user_id == uuid.UUID(user_id)).first()
                        if not is_member:
                            await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": "Not a member"}}))
                            continue
                    finally:
                        db_sub.close()
                    await manager.subscribe_channel(websocket, str(cid))
                    await websocket.send_text(json.dumps({"type": "subscribed", "payload": {"channel_id": str(cid)}}))

                elif mtype == "unsubscribe":
                    channel_id = payload.get("channel_id")
                    if channel_id:
                        await manager.unsubscribe_channel(websocket, str(channel_id))
                        await websocket.send_text(json.dumps({"type": "unsubscribed", "payload": {"channel_id": str(channel_id)}}))

                else:
                    await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": f"Unknown type {mtype}"}}))

            except WebSocketDisconnect:
                break
            except Exception as e:
                try:
                    await websocket.send_text(json.dumps({"type": "error", "payload": {"detail": str(e)}}))
                except Exception:
                    break
    finally:
        await manager.disconnect(websocket)
