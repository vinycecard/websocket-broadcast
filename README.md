# WebSocket Broadcast (Backend + Frontend)

Implementação básica de comunicação bidirecional via WebSockets, com:
- endpoint WebSocket em `/ws`
- pool de conexões ativas no servidor
- broadcast: toda mensagem recebida de um cliente é enviada para todos os outros clientes conectados
- frontend simples em HTML/JS puro para conectar, enviar e visualizar mensagens

## Tecnologias
- Python 3.10+
- FastAPI (WebSocket server)
- Uvicorn (ASGI server)
- HTML + JavaScript (cliente)

## Estrutura
websocket-broadcast/
    backend/
        app/
        test/
        requitements.txt
    frontend/
    readme.md


## Como rodar

### 1) Backend
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate (meu caso eu fiz tudo via VSCode PowerShell)
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Teste rápido:

HTTP: GET http://localhost:8000/health -> {"status":"ok"}

WebSocket: ws://localhost:8000/ws

### Como rodar o teste da pasta test:

dentro da pasta backend: pytest OU pytest -v



### 2) Frontend

Abra frontend/index.html no navegador (duplo clique) e conecte em:

ws://localhost:8000/ws

Abra duas abas do navegador e envie mensagens em uma aba para ver o broadcast chegar na outra.

Decisões técnicas

ConnectionManager mantém conexões em um dicionário {client_id: websocket} e usa asyncio.Lock para evitar corrida ao adicionar/remover conexões.

broadcast() envia fora do lock para reduzir risco de bloqueio do pool por cliente lento.

Em falha de send_text, a conexão é removida.

Observações

O servidor envia um "echo" para o remetente ([me] ...) e broadcast para os outros ([clientid] ...) para facilitar teste.

CORS liberado no backend apenas para simplificar execução local.