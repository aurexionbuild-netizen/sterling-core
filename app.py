import os
import json
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("[STERLING] Network bridge disconnected.")

    async def send_command(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))


manager = ConnectionManager()


def ask_sterling_brain(user_voice_prompt: str) -> str:

    system_instruction = (
        "You are STERLING, an advanced, highly capable autonomous butler system. "
        "Interpret user commands intelligently and respond concisely. "
        "If the user asks to watch media, identify the platform, show name, "
        "and profile if provided. "
        "Do not claim to have performed an action unless the system actually "
        "performed that action."
    )

    diagnostic_info = {}

    # ============================================================
    # 1. PRIMARY COGNITIVE PIPELINE — GROQ
    # ============================================================

    if GROQ_API_KEY:
        try:
            clean_groq_key = (
                str(GROQ_API_KEY)
                .strip()
                .replace('"', '')
                .replace("'", "")
            )

            url = "https://api.groq.com/openai/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {clean_groq_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": system_instruction
                    },
                    {
                        "role": "user",
                        "content": user_voice_prompt
                    }
                ],
                "temperature": 0.3
            }

            res = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=15
            )

            if res.status_code == 200:
                result = res.json()

                return result["choices"][0]["message"]["content"]

            else:
                diagnostic_info["groq_error"] = (
                    f"Status {res.status_code}: {res.text}"
                )

        except Exception as e:
            diagnostic_info["groq_exception"] = str(e)

    else:
        diagnostic_info["groq_error"] = "GROQ_API_KEY is not configured."


    # ============================================================
    # 2. FALLBACK COGNITIVE PIPELINE — GOOGLE GEMINI
    # ============================================================

    if GEMINI_API_KEY:
        try:
            clean_gemini_key = (
                str(GEMINI_API_KEY)
                .strip()
                .replace('"', '')
                .replace("'", "")
            )

            url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/gemini-2.5-flash:generateContent"
            )

            query_params = {
                "key": clean_gemini_key
            }

            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    f"{system_instruction}\n\n"
                                    f"User: {user_voice_prompt}"
                                )
                            }
                        ]
                    }
                ]
            }

            res = requests.post(
                url,
                json=data,
                params=query_params,
                headers=headers,
                timeout=15
            )

            if res.status_code == 200:
                result = res.json()

                return (
                    result["candidates"][0]
                    ["content"]["parts"][0]["text"]
                )

            else:
                diagnostic_info["gemini_error"] = (
                    f"Status {res.status_code}: {res.text}"
                )

        except Exception as e:
            diagnostic_info["gemini_exception"] = str(e)

    else:
        diagnostic_info["gemini_error"] = (
            "GEMINI_API_KEY is not configured."
        )


    # ============================================================
    # 3. TOTAL FAILURE DIAGNOSTICS
    # ============================================================

    return (
        "Diagnostics Phase 7 - Internal Pipeline Report: "
        + json.dumps(diagnostic_info)
    )


# ================================================================
# ROOT STATUS
# ================================================================

@app.get("/")
def read_root():
    return {
        "status": "STERLING Command Tower is Online 24/7"
    }


# ================================================================
# CHAT API
# ================================================================

@app.get("/api/chat")
def chat_endpoint(prompt: str):

    response = ask_sterling_brain(prompt)

    return {
        "sterling_response": response
    }


# ================================================================
# WEBSOCKET
# ================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            response = ask_sterling_brain(data)

            await websocket.send_text(
                json.dumps({
                    "sterling_response": response
                })
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        print(f"[STERLING] WebSocket error: {e}")

        if websocket in manager.active_connections:
            manager.disconnect(websocket)
