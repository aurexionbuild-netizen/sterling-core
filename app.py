import os
import json
import requests

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


# ============================================================
# STERLING COMMAND TOWER
# ============================================================

app = FastAPI(title="STERLING Command Tower")


# ============================================================
# API KEYS
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CONNECTION MANAGER
# ============================================================

class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        print(
            "[STERLING] New network bridge established."
        )

    def disconnect(self, websocket: WebSocket):

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        print(
            "[STERLING] Network bridge disconnected."
        )

    async def send_command(self, message: dict):

        for connection in self.active_connections:

            await connection.send_text(
                json.dumps(message)
            )


manager = ConnectionManager()


# ============================================================
# CLEAN API KEY
# ============================================================

def clean_api_key(key):

    if not key:
        return None

    return (
        str(key)
        .strip()
        .replace('"', "")
        .replace("'", "")
    )


# ============================================================
# FIND AVAILABLE GROQ MODEL
# ============================================================

def get_groq_model():

    """
    Ask Groq which models are currently available.

    This prevents STERLING from breaking when an old
    model is removed or renamed.
    """

    api_key = clean_api_key(GROQ_API_KEY)

    if not api_key:
        return None

    try:

        url = "https://api.groq.com/openai/v1/models"

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:

            print(
                f"[STERLING] Groq model discovery failed: "
                f"{response.status_code} {response.text}"
            )

            return None

        result = response.json()

        models = result.get("data", [])

        if not models:
            return None


        # Preferred models, in order.
        #
        # If these exist on the account, use them.
        # Otherwise choose another available text model.

        preferred_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]


        available_ids = [
            model.get("id")
            for model in models
            if model.get("id")
        ]


        # First try preferred models.

        for preferred in preferred_models:

            if preferred in available_ids:

                print(
                    f"[STERLING] Groq model selected: "
                    f"{preferred}"
                )

                return preferred


        # Otherwise find a likely text-generation model.

        for model_id in available_ids:

            model_lower = model_id.lower()

            if (
                "llama" in model_lower
                or "mixtral" in model_lower
                or "qwen" in model_lower
                or "gemma" in model_lower
                or "gpt" in model_lower
            ):

                print(
                    f"[STERLING] Groq fallback model selected: "
                    f"{model_id}"
                )

                return model_id


        # Last resort.

        selected = available_ids[0]

        print(
            f"[STERLING] Groq available model selected: "
            f"{selected}"
        )

        return selected


    except Exception as e:

        print(
            f"[STERLING] Groq model discovery exception: {e}"
        )

        return None


# ============================================================
# GROQ COGNITIVE PIPELINE
# ============================================================

def ask_groq(
    system_instruction: str,
    user_prompt: str
):

    api_key = clean_api_key(GROQ_API_KEY)

    if not api_key:

        return None, "GROQ_API_KEY is not configured."


    try:

        model = get_groq_model()

        if not model:

            return None, (
                "No usable Groq model was found."
            )


        url = (
            "https://api.groq.com/"
            "openai/v1/chat/completions"
        )


        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }


        data = {

            "model": model,

            "messages": [

                {
                    "role": "system",
                    "content": system_instruction
                },

                {
                    "role": "user",
                    "content": user_prompt
                }

            ],

            "temperature": 0.3,

            "max_tokens": 1000
        }


        response = requests.post(
            url,
            json=data,
            headers=headers,
            timeout=20
        )


        if response.status_code == 200:

            result = response.json()

            choices = result.get(
                "choices",
                []
            )

            if not choices:

                return None, (
                    "Groq returned no choices."
                )


            message = choices[0].get(
                "message",
                {}
            )


            content = message.get(
                "content"
            )


            if content:

                return content, None


            return None, (
                "Groq returned an empty response."
            )


        return None, (
            f"Status {response.status_code}: "
            f"{response.text}"
        )


    except Exception as e:

        return None, str(e)


# ============================================================
# GEMINI COGNITIVE PIPELINE
# ============================================================

def ask_gemini(
    system_instruction: str,
    user_prompt: str
):

    api_key = clean_api_key(GEMINI_API_KEY)

    if not api_key:

        return None, (
            "GEMINI_API_KEY is not configured."
        )


    try:

        # Current Gemini model specified by your API response.

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-3.6-flash:"
            "generateContent"
        )


        query_params = {
            "key": api_key
        }


        headers = {
            "Content-Type": "application/json"
        }


        data = {

            "system_instruction": {

                "parts": [

                    {
                        "text": system_instruction
                    }

                ]

            },

            "contents": [

                {

                    "role": "user",

                    "parts": [

                        {
                            "text": user_prompt
                        }

                    ]

                }

            ]

        }


        response = requests.post(

            url,

            json=data,

            params=query_params,

            headers=headers,

            timeout=20
        )


        if response.status_code == 200:

            result = response.json()


            candidates = result.get(
                "candidates",
                []
            )


            if not candidates:

                return None, (
                    "Gemini returned no candidates."
                )


            content = candidates[0].get(
                "content",
                {}
            )


            parts = content.get(
                "parts",
                []
            )


            if not parts:

                return None, (
                    "Gemini returned no content parts."
                )


            text = parts[0].get(
                "text"
            )


            if text:

                return text, None


            return None, (
                "Gemini returned an empty response."
            )


        return None, (
            f"Status {response.status_code}: "
            f"{response.text}"
        )


    except Exception as e:

        return None, str(e)


# ============================================================
# STERLING BRAIN
# ============================================================

def ask_sterling_brain(
    user_voice_prompt: str
) -> str:


    system_instruction = (

        "You are STERLING, an advanced autonomous "
        "digital butler and command system. "

        "Your purpose is to intelligently interpret "
        "the user's commands and provide concise, "
        "useful responses. "

        "Speak with the calm, precise and professional "
        "manner of an advanced executive butler. "

        "Understand natural language rather than requiring "
        "rigid commands. "

        "If the user asks to watch media, identify the "
        "platform, show name and profile if provided. "

        "If the user asks for an action that the software "
        "has not actually performed, do not falsely claim "
        "that it was completed. "

        "Clearly distinguish between understanding a command "
        "and actually executing it."

    )


    diagnostic_info = {}


    # ========================================================
    # PRIMARY — GROQ
    # ========================================================

    groq_response, groq_error = ask_groq(
        system_instruction,
        user_voice_prompt
    )


    if groq_response:

        print(
            "[STERLING] Response generated by Groq."
        )

        return groq_response


    if groq_error:

        diagnostic_info["groq_error"] = groq_error


    # ========================================================
    # FALLBACK — GEMINI
    # ========================================================

    gemini_response, gemini_error = ask_gemini(
        system_instruction,
        user_voice_prompt
    )


    if gemini_response:

        print(
            "[STERLING] Response generated by Gemini."
        )

        return gemini_response


    if gemini_error:

        diagnostic_info["gemini_error"] = gemini_error


    # ========================================================
    # BOTH SYSTEMS FAILED
    # ========================================================

    print(
        "[STERLING] Both cognitive pipelines failed."
    )


    return (
        "Diagnostics Phase 7 - Internal Pipeline Report: "
        + json.dumps(
            diagnostic_info,
            indent=2
        )
    )


# ============================================================
# ROOT STATUS
# ============================================================

@app.get("/")
def read_root():

    return {

        "status":
            "STERLING Command Tower is Online 24/7",

        "system":
            "STERLING",

        "cognitive_pipeline":
            "Groq → Gemini fallback",

        "websocket":
            "/ws"

    }


# ============================================================
# CHAT API
# ============================================================

@app.get("/api/chat")
def chat_endpoint(
    prompt: str
):

    response = ask_sterling_brain(
        prompt
    )


    return {

        "sterling_response":
            response

    }


# ============================================================
# WEBSOCKET API
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await manager.connect(
        websocket
    )


    try:

        while True:

            data = await websocket.receive_text()


            response = ask_sterling_brain(
                data
            )


            await websocket.send_text(

                json.dumps({

                    "sterling_response":
                        response

                })

            )


    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )


    except Exception as e:

        print(
            f"[STERLING] WebSocket error: {e}"
        )


        if websocket in manager.active_connections:

            manager.disconnect(
                websocket
            )
