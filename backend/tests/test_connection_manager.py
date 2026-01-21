import asyncio
import pytest

from app.connection_manager import ConnectionManager


class FakeWebSocket:
    """
    Mock simples de WebSocket para testes unitários.
    Registra mensagens enviadas e simula falhas.
    """
    def __init__(self, fail_on_send=False):
        self.accepted = False
        self.sent_messages = []
        self.fail_on_send = fail_on_send

    async def accept(self):
        self.accepted = True

    async def send_text(self, message: str):
        if self.fail_on_send:
            raise RuntimeError("WebSocket send failed")
        self.sent_messages.append(message)


@pytest.mark.asyncio
async def test_connect_adds_connection():
    manager = ConnectionManager()
    ws = FakeWebSocket()

    await manager.connect("client-1", ws)

    assert "client-1" in manager.active_connections
    assert ws.accepted is True


@pytest.mark.asyncio
async def test_disconnect_removes_connection():
    manager = ConnectionManager()
    ws = FakeWebSocket()

    await manager.connect("client-1", ws)
    await manager.disconnect("client-1")

    assert "client-1" not in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_sends_to_other_clients_only():
    manager = ConnectionManager()

    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    ws3 = FakeWebSocket()

    await manager.connect("c1", ws1)
    await manager.connect("c2", ws2)
    await manager.connect("c3", ws3)

    await manager.broadcast("hello", sender_id="c1")

    assert ws1.sent_messages == []              # remetente não recebe
    assert ws2.sent_messages == ["hello"]
    assert ws3.sent_messages == ["hello"]


@pytest.mark.asyncio
async def test_broadcast_removes_broken_connections():
    manager = ConnectionManager()

    ws_ok = FakeWebSocket()
    ws_fail = FakeWebSocket(fail_on_send=True)

    await manager.connect("ok", ws_ok)
    await manager.connect("fail", ws_fail)

    await manager.broadcast("test")

    # Conexão com erro deve ser removida
    assert "fail" not in manager.active_connections
    assert "ok" in manager.active_connections
