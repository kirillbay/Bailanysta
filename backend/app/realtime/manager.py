"""In-memory WebSocket manager — no Redis, MVP."""

import asyncio
import json
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # user_id -> set of websockets
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # channel_id -> set of websockets
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {}
        # websocket -> user_id mapping
        self.ws_user: Dict[WebSocket, str] = {}
        # websocket -> set of channel_ids
        self.ws_channels: Dict[WebSocket, Set[str]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        async with self.lock:
            self.user_connections.setdefault(user_id, set()).add(websocket)
            self.ws_user[websocket] = user_id
            self.ws_channels.setdefault(websocket, set())

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            user_id = self.ws_user.pop(websocket, None)
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            channels = self.ws_channels.pop(websocket, set())
            for cid in channels:
                if cid in self.channel_subscribers:
                    self.channel_subscribers[cid].discard(websocket)
                    if not self.channel_subscribers[cid]:
                        del self.channel_subscribers[cid]

    async def subscribe_channel(self, websocket: WebSocket, channel_id: str):
        async with self.lock:
            self.channel_subscribers.setdefault(channel_id, set()).add(websocket)
            self.ws_channels.setdefault(websocket, set()).add(channel_id)

    async def unsubscribe_channel(self, websocket: WebSocket, channel_id: str):
        async with self.lock:
            if channel_id in self.channel_subscribers:
                self.channel_subscribers[channel_id].discard(websocket)
            if websocket in self.ws_channels:
                self.ws_channels[websocket].discard(channel_id)

    async def broadcast_channel(self, channel_id: str, event: dict):
        async with self.lock:
            targets = list(self.channel_subscribers.get(channel_id, set()))
        if not targets:
            return
        message = json.dumps(event)
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                pass

    async def send_to_user(self, user_id: str, event: dict):
        async with self.lock:
            targets = list(self.user_connections.get(user_id, set()))
        if not targets:
            return
        message = json.dumps(event)
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()
