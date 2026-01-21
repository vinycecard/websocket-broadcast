from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
import uuid

from .connection_manager import ConnectionManager

# ✅ app PRECISA ser criado primeiro
app = FastAPI(title="WebSocket Broadcast Server")

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ favicon vem DEPOIS do app existir
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await manager.connect(client_id, websocket)

    await manager.broadcast(
        f"[server] client {client_id[:8]} connected"
    )

    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast(
                f"[{client_id[:8]}] {text}",
                sender_id=client_id
            )
            await websocket.send_text(f"[me] {text}")

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
        await manager.broadcast(
            f"[server] client {client_id[:8]} disconnected"
        )
