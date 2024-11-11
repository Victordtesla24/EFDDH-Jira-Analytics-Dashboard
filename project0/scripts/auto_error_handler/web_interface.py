from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import json
from typing import Protocol, Any

class RuntimeManagerProtocol(Protocol):
    async def process_request(self, message: str) -> str: ...
    async def initialize(self) -> bool: ...

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class WebInterface:
    def __init__(self, runtime_manager: RuntimeManagerProtocol):
        self.runtime_manager = runtime_manager
        self._app = app
        
    async def start(self):
        """Initialize web interface"""
        return self._app

    async def handle_websocket(self, websocket: WebSocket):
        await websocket.accept()
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                response = await self.runtime_manager.process_request(message['text'])
                await websocket.send_json({"text": response, "type": "system"})
        except Exception as e:
            await self.runtime_manager.error_handler.handle_error(e, 
                {"context": "websocket"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    from .runtime_manager import RuntimeManager
    runtime = RuntimeManager()
    web_interface = WebInterface(runtime)
    await web_interface.handle_websocket(websocket)