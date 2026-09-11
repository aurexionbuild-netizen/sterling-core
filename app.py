import os
import json
import requests

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


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
# LIVING VOICE ORB INTERFACE
# ============================================================

ORB_UI_HTML = """
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>STERLING Core</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            margin: 0;

            background:
                radial-gradient(
                    circle at center,
                    #101525 0%,
                    #080a12 45%,
                    #030407 100%
                );

            color: #ffffff;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                sans-serif;

            display: flex;

            flex-direction: column;

            align-items: center;

            justify-content: center;

            height: 100vh;

            overflow: hidden;
        }


        /* ====================================================
           ORB CONTAINER
           ==================================================== */

        .orb-container {

            position: relative;

            width: 300px;

            height: 300px;

            display: flex;

            align-items: center;

            justify-content: center;

            cursor: pointer;

            user-select: none;
        }


        /* ====================================================
           MAIN ORB
           ==================================================== */

        .voice-orb {

            width: 150px;

            height: 150px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    #60a5fa 0%,
                    #2563eb 45%,
                    #1e3a8a 100%
                );

            box-shadow:

                0 0 35px #2563eb,
                0 0 75px rgba(37, 99, 235, 0.55),
                inset 0 0 35px rgba(255,255,255,0.3);

            animation:
                pulse 2.5s infinite ease-in-out;

            transition:
                all 0.35s ease;

            z-index: 2;
        }


        /* ====================================================
           ORB OUTER GLOW
           ==================================================== */

        .orb-glow {

            position: absolute;

            width: 190px;

            height: 190px;

            border-radius: 50%;

            border:
                2px solid
                rgba(96, 165, 250, 0.35);

            animation:
                ripple 2.5s infinite linear;

            z-index: 1;
        }


        .orb-glow-two {

            position: absolute;

            width: 230px;

            height: 230px;

            border-radius: 50%;

            border:
                1px solid
                rgba(59, 130, 246, 0.15);

            animation:
                ripple 3.5s infinite linear;

            z-index: 1;
        }


        /* ====================================================
           ANIMATIONS
           ==================================================== */

        @keyframes pulse {

            0% {

                transform: scale(1);

                box-shadow:
                    0 0 35px #2563eb,
                    0 0 75px rgba(37,99,235,0.45),
                    inset 0 0 35px rgba(255,255,255,0.3);
            }

            50% {

                transform: scale(1.08);

                box-shadow:
                    0 0 55px #60a5fa,
                    0 0 100px rgba(96,165,250,0.55),
                    inset 0 0 45px rgba(255,255,255,0.4);
            }

            100% {

                transform: scale(1);

                box-shadow:
                    0 0 35px #2563eb,
                    0 0 75px rgba(37,99,235,0.45),
                    inset 0 0 35px rgba(255,255,255,0.3);
            }
        }


        @keyframes ripple {

            0% {

                transform: scale(0.8);

                opacity: 0.9;
            }

            100% {

                transform: scale(1.5);

                opacity: 0;
            }
        }


        /* ====================================================
           PROCESSING STATE
           ==================================================== */

        .processing {

            background:
                radial-gradient(
                    circle,
                    #f472b6 0%,
                    #db2777 45%,
                    #831843 100%
                ) !important;

            box-shadow:

                0 0 50px #ec4899,
                0 0 100px rgba(236,72,153,0.65),
                inset 0 0 35px rgba(255,255,255,0.35) !important;

            animation:
                processingPulse 0.8s infinite ease-in-out !important;
        }


        @keyframes processingPulse {

            0% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.12);
            }

            100% {
                transform: scale(1);
            }
        }


        /* ====================================================
           STATUS
           ==================================================== */

        .status-container {

            margin-top: 30px;

            width: min(700px, 90%);

            text-align: center;
        }


        .status-text {

            font-size: 1.05rem;

            letter-spacing: 4px;

            color:
                rgba(255,255,255,0.85);

            font-weight: 500;

            text-transform: uppercase;
        }


        .response-box {

            margin-top: 20px;

            width: 100%;

            font-size: 1rem;

            color:
                rgba(255,255,255,0.65);

            line-height: 1.6;

            text-align: center;

            min-height: 60px;

            transition:
                opacity 0.3s ease;
        }


        .hint {

            position: fixed;

            bottom: 25px;

            color:
                rgba(255,255,255,0.3);

            font-size: 0.75rem;

            letter-spacing: 1px;
        }


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 600px) {

            .orb-container {

                width: 260px;

                height: 260px;
            }

            .voice-orb {

                width: 130px;

                height: 130px;
            }

            .status-text {

                font-size: 0.85rem;

                letter-spacing: 3px;
            }

            .response-box {

                font-size: 0.9rem;
            }
        }

    </style>

</head>


<body>


    <div
        class="orb-container"
        id="interactionZone"
    >

        <div
            class="orb-glow-two"
        ></div>

        <div
            class="orb-glow"
        ></div>

        <div
            class="voice-orb"
            id="sterlingOrb"
        ></div>

    </div>


    <div class="status-container">

        <div
            class="status-text"
            id="statusLabel"
        >
            STERLING ONLINE
        </div>


        <div
            class="response-box"
            id="responseText"
        >
            Tap the orb to communicate with STERLING.
        </div>

    </div>


    <div class="hint">
        STERLING COMMAND TOWER
    </div>


    <script>

        const orb =
            document.getElementById(
                "sterlingOrb"
            );

        const statusLabel =
            document.getElementById(
                "statusLabel"
            );

        const responseText =
            document.getElementById(
                "responseText"
            );


        /* ====================================================
           SEND COMMAND
           ==================================================== */

        async function sendCommand(prompt) {

            statusLabel.innerText =
                "PROCESSING";

            responseText.innerText =
                "Consulting cognitive pipelines...";

            orb.classList.add(
                "processing"
            );


            try {

                const response =
                    await fetch(
                        `/api/chat?prompt=${encodeURIComponent(prompt)}`
                    );


                if (!response.ok) {

                    throw new Error(
                        `HTTP ${response.status}`
                    );
                }


                const data =
                    await response.json();


                const sterlingResponse =
                    data.sterling_response;


                if (!sterlingResponse) {

                    throw new Error(
                        "STERLING returned no response."
                    );
                }


                statusLabel.innerText =
                    "STERLING ONLINE";


                responseText.innerText =
                    sterlingResponse;


            }

            catch (error) {

                console.error(
                    "[STERLING]",
                    error
                );


                statusLabel.innerText =
                    "CORE ERROR";


                responseText.innerText =
                    "Unable to reach STERLING Command Tower.";


            }

            finally {

                orb.classList.remove(
                    "processing"
                );

            }

        }


        /* ====================================================
           ORB INTERACTION
           ==================================================== */

        orb.addEventListener(
            "click",
            async () => {

                const prompt =
                    window.prompt(
                        "Speak to STERLING:"
                    );


                if (!prompt) {

                    return;

                }


                await sendCommand(
                    prompt
                );

            }
        );

    </script>

</body>

</html>
"""


# ============================================================
# CONNECTION MANAGER
# ============================================================

class ConnectionManager:

    def __init__(self):

        self.active_connections: list[WebSocket] = []


    async def connect(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

        print(
            "[STERLING] "
            "New network bridge established."
        )


    def disconnect(
        self,
        websocket: WebSocket
    ):

        if websocket in self.active_connections:

            self.active_connections.remove(
                websocket
            )

        print(
            "[STERLING] "
            "Network bridge disconnected."
        )


    async def send_command(
        self,
        message: dict
    ):

        for connection in self.active_connections:

            await connection.send_text(
                json.dumps(message)
            )


manager = ConnectionManager()


# ============================================================
# API KEY CLEANER
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
# GROQ MODEL DISCOVERY
# ============================================================

def get_groq_model():

    api_key =
        clean_api_key(
            GROQ_API_KEY
        )


    if not api_key:

        return None


    try:

        url =
            "https://api.groq.com/openai/v1/models"


        headers = {

            "Authorization":
                f"Bearer {api_key}"

        }


        response =
            requests.get(
                url,
                headers=headers,
                timeout=10
            )


        if response.status_code != 200:

            print(
                "[STERLING] "
                f"Groq model discovery failed: "
                f"{response.status_code}"
            )

            return None


        result =
            response.json()


        models =
            result.get(
                "data",
                []
            )


        available_ids = [

            model.get("id")

            for model in models

            if model.get("id")

        ]


        if not available_ids:

            return None


        # Preferred models.

        preferred_models = [

            "llama-3.1-8b-instant",

            "llama-3.3-70b-versatile",

            "llama-3.1-70b-versatile",

            "openai/gpt-oss-120b",

            "openai/gpt-oss-20b"

        ]


        for model in preferred_models:

            if model in available_ids:

                print(
                    "[STERLING] "
                    f"Groq model selected: {model}"
                )

                return model


        # Generic fallback.

        for model in available_ids:

            lowered =
                model.lower()


            if any(

                name in lowered

                for name in [

                    "llama",
                    "qwen",
                    "gemma",
                    "gpt"

                ]

            ):

                print(
                    "[STERLING] "
                    f"Groq fallback model: {model}"
                )

                return model


        return available_ids[0]


    except Exception as error:

        print(
            "[STERLING] "
            f"Groq discovery exception: {error}"
        )

        return None


# ============================================================
# GROQ BRAIN
# ============================================================

def ask_groq(
    system_instruction,
    user_prompt
):

    api_key =
        clean_api_key(
            GROQ_API_KEY
        )


    if not api_key:

        return (
            None,
            "GROQ_API_KEY is not configured."
        )


    try:

        model =
            get_groq_model()


        if not model:

            return (
                None,
                "No available Groq model was found."
            )


        url =
            "https://api.groq.com/openai/v1/chat/completions"


        headers = {

            "Authorization":
                f"Bearer {api_key}",

            "Content-Type":
                "application/json"

        }


        data = {

            "model": model,

            "messages": [

                {

                    "role":
                        "system",

                    "content":
                        system_instruction

                },

                {

                    "role":
                        "user",

                    "content":
                        user_prompt

                }

            ],

            "temperature":
                0.3,

            "max_tokens":
                1000

        }


        response =
            requests.post(

                url,

                json=data,

                headers=headers,

                timeout=20

            )


        if response.status_code != 200:

            return (

                None,

                f"Status {response.status_code}: "
                f"{response.text}"

            )


        result =
            response.json()


        choices =
            result.get(
                "choices",
                []
            )


        if not choices:

            return (
                None,
                "Groq returned no choices."
            )


        content =
            choices[0][
                "message"
            ].get(
                "content"
            )


        if not content:

            return (
                None,
                "Groq returned empty content."
            )


        return (
            content,
            None
        )


    except Exception as error:

        return (
            None,
            str(error)
        )


# ============================================================
# GEMINI BRAIN
# ============================================================

def ask_gemini(
    system_instruction,
    user_prompt
):

    api_key =
        clean_api_key(
            GEMINI_API_KEY
        )


    if not api_key:

        return (
            None,
            "GEMINI_API_KEY is not configured."
        )


    try:

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/"
            "gemini-3.6-flash:"
            "generateContent"
        )


        headers = {

            "Content-Type":
                "application/json"

        }


        params = {

            "key":
                api_key

        }


        data = {

            "system_instruction": {

                "parts": [

                    {

                        "text":
                            system_instruction

                    }

                ]

            },

            "contents": [

                {

                    "role":
                        "user",

                    "parts": [

                        {

                            "text":
                                user_prompt

                        }

                    ]

                }

            ]

        }


        response =
            requests.post(

                url,

                json=data,

                params=params,

                headers=headers,

                timeout=20

            )


        if response.status_code != 200:

            return (

                None,

                f"Status {response.status_code}: "
                f"{response.text}"

            )


        result =
            response.json()


        candidates =
            result.get(
                "candidates",
                []
            )


        if not candidates:

            return (
                None,
                "Gemini returned no candidates."
            )


        parts =
            candidates[0].get(
                "content",
                {}
            ).get(
                "parts",
                []
            )


        if not parts:

            return (
                None,
                "Gemini returned no content."
            )


        text =
            parts[0].get(
                "text"
            )


        if not text:

            return (
                None,
                "Gemini returned empty content."
            )


        return (
            text,
            None
        )


    except Exception as error:

        return (
            None,
            str(error)
        )


# ============================================================
# STERLING BRAIN
# ============================================================

def ask_sterling_brain(
    user_voice_prompt: str
) -> str:


    system_instruction = (

        "You are STERLING, an advanced autonomous "
        "digital butler and command system. "

        "Your personality is calm, intelligent, "
        "precise, professional and composed. "

        "Interpret natural-language commands intelligently. "

        "Respond concisely unless the user asks for detail. "

        "You are the cognitive layer of a larger command "
        "and automation system. "

        "Do not claim to have performed an action unless "
        "the system has actually performed it. "

        "If a command requires an external action that "
        "has not yet been connected, explain what would "
        "need to happen rather than pretending it happened. "

        "If the user asks to watch media, identify the "
        "platform, show name and profile if provided."

    )


    diagnostics = {}


    # ========================================================
    # PRIMARY: GROQ
    # ========================================================

    groq_response, groq_error = ask_groq(

        system_instruction,

        user_voice_prompt

    )


    if groq_response:

        print(
            "[STERLING] "
            "Primary cognitive response: GROQ"
        )

        return groq_response


    diagnostics[
        "groq_error"
    ] = groq_error


    # ========================================================
    # FALLBACK: GEMINI
    # ========================================================

    gemini_response, gemini_error = ask_gemini(

        system_instruction,

        user_voice_prompt

    )


    if gemini_response:

        print(
            "[STERLING] "
            "Fallback cognitive response: GEMINI"
        )

        return gemini_response


    diagnostics[
        "gemini_error"
    ] = gemini_error


    # ========================================================
    # FAILURE REPORT
    # ========================================================

    print(
        "[STERLING] "
        "Both cognitive pipelines failed."
    )


    return (

        "STERLING Core Pipeline Interruption.\n\n"

        + json.dumps(
            diagnostics,
            indent=2
        )

    )


# ============================================================
# ROOT UI
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)

def read_root():

    return ORB_UI_HTML


# ============================================================
# CHAT API
# ============================================================

@app.get("/api/chat")

def chat_endpoint(
    prompt: str
):

    response =
        ask_sterling_brain(
            prompt
        )


    return {

        "sterling_response":
            response

    }


# ============================================================
# WEBSOCKET
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

            data =
                await websocket.receive_text()


            response =
                ask_sterling_brain(
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


    except Exception as error:

        print(
            "[STERLING] "
            f"WebSocket error: {error}"
        )


        manager.disconnect(
            websocket
        )
