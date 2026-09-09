import os
import json
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI(title="STERLING Command Tower")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ConnectionManager:
    def __init__(self):
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
    system_instruction = (
        "You are STERLING, an advanced, highly capable autonomous butler system. "
        "Interpret user commands flawlessly. If they ask to watch media, extract the "
        "platform, show name, and profile. Respond concisely."
    )
    
    diagnostic_info = {}

    # 1. Try Groq (Production Model ID)
    if GROQ_API_KEY:
        try:
            clean_groq_key = str(GROQ_API_KEY).strip().replace('"', '').replace("'", "")
            url = "https://groq.com"
            headers = {
                "Authorization": f"Bearer {clean_groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.1-8b-instant",  # Standard production model ID
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_voice_prompt}
                ]
            }
            res = requests.post(url, json=data, headers=headers, timeout=5)
            if res.status_code == 200:
                return res.json()['choices']['message']['content']
            else:
                diagnostic_info["groq_error"] = f"Status {res.status_code}: {res.text}"
        except Exception as e:
            diagnostic_info["groq_exception"] = str(e)

    # 2. Fallback to Gemini (Updated API URL Layout)
    if GEMINI_API_KEY:
        try:
            clean_gemini_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")
            # FIXED: Updated URL pattern layout for Gemini models
            url = "https://googleapis.com"
            query_params = {"key": clean_gemini_key}
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": f"{system_instruction}\n\nUser: {user_voice_prompt}"}]
                }]
            }
            res = requests.post(url, json=data, params=query_params, headers=headers, timeout=5)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                diagnostic_info["gemini_error"] = f"Status {res.status_code}: {res.text}"
        except Exception as e:
            diagnostic_info["gemini_exception"] = str(e)
            
    return f"Diagnostics Phase 3 - Raw Pipeline Responses: {json.dumps(diagnostic_info)}"

@app.get("/")
def read_root():
    return {"status": "STERLING Command Tower is Online 24/7"}

@app.get("/api/chat")
def chat_endpoint(prompt: str):
    response = ask_sterling_brain(prompt)
    return {"sterling_response": response}

@app.post("/api/play-media")
async def play_media(request: MediaRequest):
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
    print(f"[STERLING] Received network update packet: {log.devices}")
    return {"status": "Topology catalogued successfully"}

@app.websocket("/ws/network-bridge")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "NETWORK_CATALOGUE":
                print("[STERLING] Network update captured via socket link.")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
