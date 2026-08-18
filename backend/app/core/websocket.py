from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections per chat room.

    Keeps track of active websockets per `chat_id` and allows broadcasting
    messages to all connected sockets in the same chat.
    """

    def __init__(self) -> None:
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        conns = self.active.get(chat_id)
        if conns is None:
            conns = set()
            self.active[chat_id] = conns
        conns.add(websocket)

    def disconnect(self, chat_id: str, websocket: WebSocket) -> None:
        conns = self.active.get(chat_id)
        if not conns:
            return
        try:
            conns.remove(websocket)
        except KeyError:
            pass
        if len(conns) == 0:
            self.active.pop(chat_id, None)

    async def broadcast(self, chat_id: str, message: dict) -> None:
        conns = self.active.get(chat_id) or set()
        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                # ignore send errors; caller may cleanup on disconnect
                pass


manager = ConnectionManager()
