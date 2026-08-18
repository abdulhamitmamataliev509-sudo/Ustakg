"""Chat / messaging endpoints and WebSocket endpoint.

Provides listing of chats, fetching chat messages and a WebSocket
endpoint for real-time messaging. WebSocket connections are authenticated
via a `token` query parameter (JWT access token).
"""
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.websocket import manager
from app.api.deps import get_current_user
from app.models.chat import Chat, ChatMessage
from app.models.user import User
from app.models.master import MasterProfile

router = APIRouter()


@router.get("/", response_model=list)
def list_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	"""List chats for the current user (customer or master)."""
	if current_user.role.name == "MASTER":
		# find the master profile belonging to this user
		profile = db.query(MasterProfile).filter(MasterProfile.user_id == current_user.id).first()
		if profile:
			chats = db.query(Chat).filter((Chat.master_id == profile.id) | (Chat.customer_id == current_user.id)).all()
		else:
			chats = db.query(Chat).filter(Chat.customer_id == current_user.id).all()
	else:
		chats = db.query(Chat).filter(Chat.customer_id == current_user.id).all()
	out = []
	for c in chats:
		out.append({
			"id": str(c.id),
			"order_id": str(c.order_id) if c.order_id else None,
			"customer_id": str(c.customer_id),
			"master_id": str(c.master_id),
			"created_at": c.created_at.isoformat(),
		})
	return out


@router.get("/{chat_id}/messages", response_model=list)
def get_chat_messages(chat_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	"""Return messages for a chat if the user participates in it."""
	chat = db.get(Chat, chat_id)
	if chat is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
	# participant check: customer or master user
	participant = False
	if chat.customer_id == current_user.id:
		participant = True
	else:
		profile = db.query(MasterProfile).filter(MasterProfile.id == chat.master_id).first()
		if profile and profile.user_id == current_user.id:
			participant = True
	if not participant:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a chat participant")
	messages = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(ChatMessage.created_at.asc()).all()
	out = []
	for m in messages:
		out.append({
			"id": str(m.id),
			"chat_id": str(m.chat_id),
			"sender_id": str(m.sender_id),
			"message_text": m.message_text,
			"is_read": m.is_read,
			"created_at": m.created_at.isoformat(),
		})
	return out


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
	"""WebSocket endpoint for live chat. Authenticate via `token` query param."""
	token = websocket.query_params.get("token")
	if not token:
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
		return
	# decode token
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		user_id = payload.get("sub")
		if payload.get("type") != "access":
			await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
			return
	except Exception:
		await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
		return

	# validate chat exists and user participates
	db = SessionLocal()
	try:
		try:
			cid = uuid.UUID(chat_id)
		except Exception:
			await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
			return
		chat = db.get(Chat, cid)
		if chat is None:
			await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
			return
		# user must be either customer or master (master -> check profile.user_id)
		user_participates = False
		if str(chat.customer_id) == str(user_id):
			user_participates = True
		else:
			# check master profile -> match user id
			from app.models.master import MasterProfile

			master_profile = db.get(MasterProfile, chat.master_id)
			if master_profile and str(master_profile.user_id) == str(user_id):
				user_participates = True
		if not user_participates:
			await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
			return

		await manager.connect(chat_id, websocket)
		# notify connected
		await manager.broadcast(chat_id, {"type": "system", "message": "joined"})

		while True:
			data = await websocket.receive_json()
			# expect {'message_text': '...'}
			text = data.get("message_text")
			if not text:
				continue
			# save to DB
			msg = ChatMessage(chat_id=chat.id, sender_id=user_id, message_text=text)
			db.add(msg)
			db.commit()
			db.refresh(msg)
			payload = {
				"type": "message",
				"id": str(msg.id),
				"chat_id": str(msg.chat_id),
				"sender_id": str(msg.sender_id),
				"message_text": msg.message_text,
				"created_at": msg.created_at.isoformat(),
			}
			await manager.broadcast(chat_id, payload)
	except WebSocketDisconnect:
		manager.disconnect(chat_id, websocket)
	finally:
		db.close()

