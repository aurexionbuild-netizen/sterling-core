import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json

app = FastAPI(title="STERLING Command Tower")

# Track active network bridge connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] =

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("[STERLING] New network bridge established filelessly.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("[STERLING] Network bridge disconnected.")

    async def send_command(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

class MediaRequest(BaseModel):
    content: str
    platform: str
    profile: str

@app.get("/")
def read_root():
    return {"status": "STERLING Command Tower is Online 24/7"}

# Endpoint to trigger high-level media playback commands
@app.post("/api/play-media")
async def play_media(request: MediaRequest):
    print(f"[STERLING] Interpreting intent: Play '{request.content}' on {request.platform} (Profile: {request.profile})")
    
    # Package the automation instructions to stream down the active network bridge
    payload = {
        "action": "LAUNCH_MEDIA",
        "platform": request.platform,
        "content": request.content,
        "profile": request.profile
    }
    
    # Push the command down to the active local network connection
    await manager.send_command(payload)
    return {"status": "Command streamed to local network injection queue"}

# The live tunnel endpoint for whatever Wi-Fi network you are connected to
@websocket("/ws/network-bridge")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Listen for incoming data from the automated local network scan
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "NETWORK_CATALOGUE":
                print("[STERLING] Received silent network scan data:")
                print(json.dumps(message.get("devices"), indent=2))
                # Trigger for UI to morph into status map goes here
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
