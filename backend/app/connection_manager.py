from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict
from fastapi import WebSocket


@dataclass
class ConnectionManager:
    """
    Mantém um pool de conexões WebSocket ativas.
    - connect(): aceita a conexão e registra
    - disconnect(): remove do pool
    - broadcast(): envia para todos, exceto opcionalmente o emissor
    """
    active_connections: Dict[str, WebSocket] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str) -> None:
        async with self._lock:
            self.active_connections.pop(client_id, None)

    async def broadcast(self, message: str, sender_id: str | None = None) -> None:
        async with self._lock:
            targets = [
                (cid, ws)
                for cid, ws in self.active_connections.items()
                if cid != sender_id
            ]

        # Envia fora do lock para não travar o pool caso um client demore
        for cid, ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                # Se falhar, remove conexão quebrada
                await self.disconnect(cid)
