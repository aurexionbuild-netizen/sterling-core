import os
import json
import urllib.request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="STERLING Command Tower")

# Fetch keys from Render Environment Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Track active network bridge connections
class ConnectionManager:
    def __init__(self):
        # FIXED: Added the missing brackets [] here
        self.active_connections: list[WebSocket] = []

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

class NetworkLog(BaseModel):
    type: str
    devices: list

def ask_sterling_brain(user_voice_prompt: str) -> str:
    """Processes user voice prompts using Groq speed, falling back to Gemini."""
    system_instruction = (
        "You are STERLING, an advanced, highly capable autonomous butler system. "
        "Interpret user commands flawlessly. If they ask to watch media, extract the "
        "platform, show name, and profile. Respond concisely."
    )
    
    # 1. Try Primary Engine: Groq (Llama 3.3)
    if GROQ_API_KEY:
        try:
            url = "https://groq.com"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-specdec",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_voice_prompt}
                ]
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['choices']['message']['content']
        except Exception as e:
            print(f"[STERLING Engine] Groq primary failed: {e}. Shifting to Gemini fallback...")

    # 2. Fallback Engine: Google Gemini
    if GEMINI_API_KEY:
        try:
            url = f"https://googleapis.com{GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\nUser: {user_voice_prompt}"}]}]
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['candidates']['content']['parts']['text']
        except Exception as e:
            print(f"[STERLING Engine] Gemini fallback failed: {e}")
            
    return "Sterling Core System Error: Both cognitive AI pipelines are unresponsive."

@app.get("/")
def read_root():
    return {"status": "STERLING Command Tower is Online 24/7"}

@app.get("/api/chat")
def chat_endpoint(prompt: str):
    response = ask_sterling_brain(prompt)
    return {"sterling_response": response}

@app.post("/api/play-media")
async def play_media(request: MediaRequest):
    print(f"[STERLING] Interpreting intent: Play '{request.content}' on {request.platform} (Profile: {request.profile})")
    payload = {
        "action": "LAUNCH_MEDIA",
        "platform": request.platform,
        "content": request.content,
        "profile": request.profile
    }
    await manager.send_command(payload)
    return {"status": "Command streamed to local network injection queue"}

@app.post("/api/register-network")
async def register_network(log: NetworkLog):
    print("[STERLING] Received silent network scan data:")
    print(json.dumps(log.devices, indent=2))
    return {"status": "Topology catalogued successfully"}

# FIXED: Corrected standard FastAPI router signature
@app.websocket("/ws/network-bridge")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "NETWORK_CATALOGUE":
                print("[STERLING] Received live WebSocket network data update")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
