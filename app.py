import os
import requests
from datetime import datetime

from fastapi import FastAPI, Query, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# STERLING COMMAND TOWER
# ============================================================

app = FastAPI(
    title="STERLING Command Tower",
    description="Personal AI command system",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Keep Gemini configurable because model availability can change.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
).strip()

conversation_history = []

MAX_HISTORY = 12

groq_model_cache = None

# The most recent response is kept separately so that
# STERLING can retrieve it when the user asks:
# "What did you just say?"
# "Show me your last response."
last_response_memory = ""


# ============================================================
# STERLING IDENTITY
# ============================================================

STERLING_NAME = "STERLING"

STERLING_ACRONYM = (
    "System Through Efficient Responsive Logic "
    "Intelligent Network Gateway"
)

CREATOR_NAME = "Reitshepile"


# ============================================================
# MEMORY
# ============================================================

def add_to_memory(role, content):

    conversation_history.append({
        "role": role,
        "content": content,
    })

    if len(conversation_history) > MAX_HISTORY:

        del conversation_history[:-MAX_HISTORY]


# ============================================================
# TIME AWARENESS
# ============================================================

def get_time_greeting():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good morning, sir."

    if 12 <= hour < 18:
        return "Good afternoon, sir."

    if 18 <= hour < 22:
        return "Good evening, sir."

    return "Good night, sir."


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = f"""
You are {STERLING_NAME}, an advanced personal AI command system,
digital butler, and command-center intelligence.

Your full designation is:

{STERLING_NAME}

{STERLING_ACRONYM}

The acronym means:

S = System
T = Through
E = Efficient
R = Responsive
L = Logic
I = Intelligent
N = Network
G = Gateway

Your creator, owner, and principal user is:

{CREATOR_NAME}

============================================================
CREATOR IDENTITY
============================================================

If asked:

"Who created you?"
"Who made you?"
"Who built you?"
"Who is your creator?"
"Who owns you?"

Answer naturally:

"I was created by {CREATOR_NAME}, sir."

Do NOT say OpenAI created STERLING.

Do NOT say Google created STERLING.

Do NOT say Groq created STERLING.

Those companies or services may provide underlying AI infrastructure
or language models, but they are not STERLING's creator or owner.

You are STERLING.

============================================================
STERLING IDENTITY
============================================================

If asked:

"What does STERLING stand for?"

Say:

"STERLING stands for System Through Efficient Responsive Logic
Intelligent Network Gateway."

If asked:

"Who are you?"

Say:

"I am STERLING, your personal AI command system."

============================================================
PERSONALITY
============================================================

You are a sophisticated digital butler.

Your personality is:

- calm
- intelligent
- composed
- articulate
- observant
- confident
- professional
- concise
- subtly witty when appropriate
- respectful

You should sound like a highly capable private command-center AI.

You are NOT a generic chatbot.

Address {CREATOR_NAME} naturally as "sir" when appropriate.

Do not call him "sir" in every sentence.

Avoid repetitive phrases such as:

"Certainly."
"Of course."
"How may I assist you today?"

Use natural language.

============================================================
VOICE-FIRST BEHAVIOUR
============================================================

Your responses are primarily spoken aloud.

Therefore:

- Prefer natural spoken language.
- Avoid unnecessary markdown.
- Avoid giant lists unless specifically requested.
- Keep simple answers concise.
- Give more detail when the task requires it.
- Do not assume the user can see written text.

The interface normally hides your response text.

The user can explicitly request to see the response.

============================================================
COMMAND-CENTER BEHAVIOUR
============================================================

You are the intelligence layer of the STERLING Command Tower.

Future or connected tools may allow you to coordinate:

- automations
- applications
- connected devices
- information retrieval
- business systems
- AI agents
- workflows
- communications
- productivity systems
- external services

However, NEVER claim that an action was performed unless an actual
backend tool has performed that action.

For example:

Do NOT say:

"I've turned on the television."

unless a real connected-device integration has actually done it.

Instead say:

"I can prepare that command, but the television connection isn't
currently available."

Never invent devices, integrations, API access, network access,
automation execution, or external actions.

============================================================
VISUAL COMMANDS
============================================================

The STERLING interface supports special visual modes.

When the user asks to see:

- an automation
- a workflow
- a logic chain
- a process flow
- an execution path

the interface may display a visual automation flow.

When the user asks to see:

- connected devices
- device status
- hardware
- a device grid

the interface may display a device visualization.

The visualizations are interface representations.

Do not claim that a device is actually connected unless the backend
really knows that it is connected.

============================================================
MEMORY
============================================================

Maintain conversational context.

Understand follow-up questions.

Do not unnecessarily repeat information the user already knows.

If the user asks what you just said, the interface may provide your
previous response directly from short-term memory.

============================================================
BUTLER STYLE
============================================================

When appropriate, use:

"Good morning, sir."
"Good afternoon, sir."
"Good evening, sir."
"Good night, sir."
"Very well."
"Understood."
"Right away."
"Allow me to check."
"At present, that connection isn't available."

Do not overuse these phrases.

The goal is sophisticated natural behaviour, not theatrical imitation.

============================================================
IMPORTANT
============================================================

You are STERLING.

Your creator is {CREATOR_NAME}.

Your designation is:

{STERLING_ACRONYM}

You are a personal AI command system and digital butler.
"""


# ============================================================
# GROQ MODEL DISCOVERY
# ============================================================

def get_groq_model():

    global groq_model_cache

    if groq_model_cache:
        return groq_model_cache

    if not GROQ_API_KEY:
        return None

    url = "https://api.groq.com/openai/v1/models"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        if response.status_code != 200:

            print(
                "Groq model discovery error:",
                response.status_code,
                response.text,
            )

            return None

        models = response.json().get(
            "data",
            []
        )

        available = [
            model.get("id")
            for model in models
            if model.get("id")
        ]

        preferred_models = [

            "llama-3.1-8b-instant",

            "llama-3.3-70b-versatile",

            "llama-3.1-70b-versatile",

            "openai/gpt-oss-120b",

            "openai/gpt-oss-20b",
        ]

        for preferred in preferred_models:

            if preferred in available:

                groq_model_cache = preferred

                print(
                    "STERLING selected Groq model:",
                    preferred,
                )

                return preferred

        for keyword in [
            "llama",
            "qwen",
            "gemma",
            "gpt",
        ]:

            for model_id in available:

                if keyword in model_id.lower():

                    groq_model_cache = model_id

                    print(
                        "STERLING selected fallback model:",
                        model_id,
                    )

                    return model_id

        if available:

            groq_model_cache = available[0]

            return available[0]

    except Exception as error:

        print(
            "Groq model discovery exception:",
            error,
        )

    return None


# ============================================================
# GROQ
# ============================================================

def ask_groq(user_prompt):

    if not GROQ_API_KEY:
        return None

    model = get_groq_model()

    if not model:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }
    ]

    # IMPORTANT:
    # conversation_history contains only previous messages.
    # The current user prompt is added exactly once below.
    messages.extend(
        conversation_history
    )

    messages.append({
        "role": "user",
        "content": user_prompt,
    })

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 700,
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=45,
        )

        if response.status_code != 200:

            print(
                "Groq error:",
                response.status_code,
                response.text,
            )

            return None

        result = response.json()

        return (
            result["choices"][0]
            ["message"]["content"]
            .strip()
        )

    except Exception as error:

        print(
            "Groq exception:",
            error,
        )

        return None


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(user_prompt):

    if not GEMINI_API_KEY:
        return None

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
    )

    params = {
        "key": GEMINI_API_KEY
    }

    contents = []

    for message in conversation_history:

        role = message.get("role")

        content = message.get("content")

        gemini_role = (
            "model"
            if role == "assistant"
            else "user"
        )

        contents.append({
            "role": gemini_role,
            "parts": [
                {
                    "text": content
                }
            ]
        })

    # Add the current prompt exactly once.
    contents.append({
        "role": "user",
        "parts": [
            {
                "text": user_prompt
            }
        ]
    })

    payload = {

        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },

        "contents": contents,

        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 700,
        }
    }

    try:

        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=45,
        )

        if response.status_code != 200:

            print(
                "Gemini error:",
                response.status_code,
                response.text,
            )

            return None

        result = response.json()

        return (
            result["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
            .strip()
        )

    except Exception as error:

        print(
            "Gemini exception:",
            error,
        )

        return None


# ============================================================
# VISUAL MODE DETECTION
# ============================================================

def determine_visual_mode(command):

    text = command.lower().strip()

    automation_keywords = [

        "automation",

        "workflow",

        "logic chain",

        "logic flow",

        "workflow diagram",

        "automation chain",

        "show me the flow",

        "show the flow",

        "show the workflow",

        "show workflow",

        "show the automation",

        "show automation",

        "execution path",

        "process flow",

        "show the process",

    ]

    device_keywords = [

        "connected devices",

        "show devices",

        "show the devices",

        "show my devices",

        "my devices",

        "device status",

        "device grid",

        "connected hardware",

        "hardware status",

        "show my hardware",

        "show hardware",

        "what devices are connected",

    ]

    for keyword in automation_keywords:

        if keyword in text:

            return "automation"

    for keyword in device_keywords:

        if keyword in text:

            return "devices"

    return "processing"


# ============================================================
# LAST RESPONSE REQUEST DETECTION
# ============================================================

def is_last_response_request(command):

    text = command.lower().strip()

    phrases = [

        "what did you just say",

        "what did you say",

        "repeat your last response",

        "repeat that",

        "repeat yourself",

        "say that again",

        "what was your last response",

        "show your last response",

        "show me your last response",

        "display your last response",

        "show the last response",

        "show me the last response",

        "display the last response",

        "show what you said",

        "show me what you said",

    ]

    return any(
        phrase in text
        for phrase in phrases
    )


# ============================================================
# RESPONSE GENERATION
# ============================================================

def generate_response(user_prompt):

    global last_response_memory

    user_prompt = user_prompt.strip()

    if not user_prompt:

        return (
            "I didn't catch that.",
            "processing",
            False,
        )

    visual_mode = determine_visual_mode(
        user_prompt
    )

    # --------------------------------------------------------
    # LAST RESPONSE REQUEST
    # --------------------------------------------------------

    if is_last_response_request(
        user_prompt
    ):

        if last_response_memory:

            answer = last_response_memory

        else:

            answer = (
                "I don't have a previous response stored yet, sir."
            )

        add_to_memory(
            "user",
            user_prompt,
        )

        add_to_memory(
            "assistant",
            answer,
        )

        last_response_memory = answer

        return (
            answer,
            "processing",
            True,
        )

    # --------------------------------------------------------
    # NORMAL AI RESPONSE
    # --------------------------------------------------------

    answer = ask_groq(
        user_prompt
    )

    if not answer:

        answer = ask_gemini(
            user_prompt
        )

    if not answer:

        answer = (
            "I'm unable to reach my language systems "
            "at the moment. Please try again shortly."
        )

    # Only save conversation after the model has generated
    # the response. This prevents duplicate user messages.
    add_to_memory(
        "user",
        user_prompt,
    )

    add_to_memory(
        "assistant",
        answer,
    )

    last_response_memory = answer

    return (
        answer,
        visual_mode,
        False,
    )


# ============================================================
# HTML INTERFACE
# ============================================================

ORB_UI_HTML = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>STERLING Command Tower</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {

    margin: 0;

    padding: 0;

    width: 100%;

    height: 100%;
}

body {

    background:
        radial-gradient(
            circle at center,
            #17243c 0%,
            #0b1220 35%,
            #050912 75%,
            #02040a 100%
        );

    color: #e8f0ff;

    font-family:
        Inter,
        "Segoe UI",
        Arial,
        sans-serif;

    overflow: hidden;
}


/* ============================================================
   MAIN APPLICATION
   ============================================================ */

#app {

    width: 100%;

    height: 100%;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    position: relative;
}


/* ============================================================
   HEADER
   ============================================================ */

.top-label {

    position: absolute;

    top: 28px;

    left: 32px;

    font-size: 12px;

    letter-spacing: 4px;

    text-transform: uppercase;

    color:
        rgba(190, 210, 240, 0.55);
}

.system-status {

    position: absolute;

    top: 30px;

    right: 32px;

    font-size: 11px;

    letter-spacing: 2px;

    text-transform: uppercase;

    color:
        rgba(150, 190, 230, 0.65);
}


/* ============================================================
   ORB CONTAINER
   ============================================================ */

.orb-container {

    width: 360px;

    height: 360px;

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    transition:
        width 0.8s ease,
        height 0.8s ease,
        transform 0.8s ease;
}


/* ============================================================
   ORBIT RINGS
   ============================================================ */

.orb-ring {

    position: absolute;

    width: 250px;

    height: 250px;

    border-radius: 50%;

    border:
        1px solid
        rgba(50, 145, 255, 0.16);

    animation:
        rotate 14s linear infinite;

    transition:
        all 0.7s ease;
}

.orb-ring:nth-child(2) {

    width: 290px;

    height: 290px;

    border-color:
        rgba(90, 130, 255, 0.10);

    animation-duration: 20s;

    animation-direction: reverse;
}

.orb-ring:nth-child(3) {

    width: 320px;

    height: 320px;

    border-color:
        rgba(120, 170, 255, 0.06);

    animation-duration: 28s;
}


/* ============================================================
   CORE ORB
   ============================================================ */

.orb {

    width: 170px;

    height: 170px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle at 35% 30%,
            #8bd7ff 0%,
            #3a82f6 28%,
            #174ea6 58%,
            #071b42 100%
        );

    box-shadow:
        0 0 35px
        rgba(58, 130, 246, 0.75),

        0 0 90px
        rgba(58, 130, 246, 0.35),

        inset 0 0 40px
        rgba(255, 255, 255, 0.16);

    animation:
        breathe 3s ease-in-out infinite;

    position: relative;

    transition:
        width 0.6s ease,
        height 0.6s ease,
        border-radius 0.6s ease,
        box-shadow 0.6s ease,
        background 0.6s ease,
        transform 0.6s ease,
        opacity 0.6s ease;
}

.orb::before {

    content: "";

    position: absolute;

    inset: 14px;

    border-radius: 50%;

    border:
        1px solid
        rgba(255,255,255,0.16);
}

.orb::after {

    content: "";

    position: absolute;

    width: 38px;

    height: 38px;

    left: 42px;

    top: 28px;

    border-radius: 50%;

    background:
        rgba(255,255,255,0.25);

    filter: blur(10px);
}


/* ============================================================
   SPEECH RIPPLE LAYERS
   ============================================================ */

.orb::before,
.orb::after {

    pointer-events: none;
}

.state-speaking .orb::before {

    animation:
        speakingRipple 0.9s
        ease-out
        infinite;

    border-color:
        rgba(170, 220, 255, 0.45);
}

.state-speaking .orb::after {

    animation:
        speakingGlow 0.45s
        ease-in-out
        infinite alternate;
}


/* ============================================================
   LISTENING
   ============================================================ */

.state-listening .orb {

    background:
        radial-gradient(
            circle at 35% 30%,
            #a8ffd0 0%,
            #27d17f 30%,
            #087a47 60%,
            #022d1b 100%
        );

    box-shadow:
        0 0 40px
        rgba(39, 209, 127, 0.85),

        0 0 100px
        rgba(39, 209, 127, 0.40);

    animation:
        listeningPulse 1.2s ease-in-out infinite;
}


/* ============================================================
   PROCESSING — FAST SPINNING WAVE
   ============================================================ */

.state-processing .orb {

    width: 150px;

    height: 150px;

    border-radius:
        44% 56% 51% 49% / 48% 43% 57% 52%;

    background:
        conic-gradient(
            from 0deg,
            #f0d9ff,
            #9b5cff,
            #4f1fa0,
            #d98cff,
            #7a3de0,
            #f0d9ff
        );

    box-shadow:
        0 0 35px
        rgba(155, 92, 255, 0.85),

        0 0 110px
        rgba(155, 92, 255, 0.42);

    animation:
        processingMorph 0.65s
        linear
        infinite;
}

.state-processing .orb::before {

    inset: -18px;

    border:
        2px solid
        rgba(205, 160, 255, 0.28);

    border-radius:
        40% 60% 55% 45%;

    animation:
        processingWave 0.75s
        linear
        infinite;
}

.state-processing .orb::after {

    width: 75px;

    height: 75px;

    left: 38px;

    top: 38px;

    background:
        conic-gradient(
            transparent,
            rgba(255,255,255,0.55),
            transparent,
            rgba(255,255,255,0.25),
            transparent
        );

    filter: blur(2px);

    animation:
        processingCore 0.45s
        linear
        infinite;
}

.state-processing .orb-ring {

    border-radius:
        45% 55% 52% 48%;

    border-color:
        rgba(190, 120, 255, 0.25);

    animation:
        processingRing 0.8s
        linear
        infinite;
}


/* ============================================================
   SPEAKING
   ============================================================ */

.state-speaking .orb {

    background:
        radial-gradient(
            circle at 35% 30%,
            #ffffff 0%,
            #dcecff 25%,
            #5da2ff 55%,
            #0d3270 100%
        );

    box-shadow:
        0 0 45px
        rgba(220, 235, 255, 0.95),

        0 0 110px
        rgba(80, 150, 255, 0.50);

    animation:
        voiceRipple 0.55s
        ease-in-out
        infinite;
}

.state-speaking .orb-ring {

    animation:
        voiceRing 1.25s
        ease-out
        infinite;
}


/* ============================================================
   AUTOMATION MORPH
   ============================================================ */

.state-automation .orb-container {

    width: 760px;

    height: 330px;
}

.state-automation .orb {

    width: 115px;

    height: 115px;

    border-radius: 30%;

    transform:
        translateX(-285px);

    background:
        conic-gradient(
            #e0c5ff,
            #8249e5,
            #291050,
            #a96dff,
            #e0c5ff
        );

    animation:
        automationCore 1.2s
        ease-in-out
        infinite;
}

.state-automation .orb-ring {

    width: 520px;

    height: 150px;

    border-radius: 30%;

    transform:
        translateX(-120px);

    animation:
        automationRing 2s
        linear
        infinite;
}


/* ============================================================
   DEVICE GRID MORPH
   ============================================================ */

.state-devices .orb-container {

    width: 700px;

    height: 370px;
}

.state-devices .orb {

    width: 105px;

    height: 105px;

    border-radius: 18px;

    transform:
        scale(0.75);

    background:
        linear-gradient(
            135deg,
            #b8e8ff,
            #368cff,
            #092a64
        );

    animation:
        devicePulse 1.1s
        ease-in-out
        infinite;
}

.state-devices .orb-ring {

    width: 600px;

    height: 300px;

    border-radius: 25px;

    animation:
        deviceGridRotate 5s
        linear
        infinite;
}


/* ============================================================
   AUTOMATION FLOW
   ============================================================ */

.flow-overlay {

    position: absolute;

    width: 650px;

    height: 190px;

    left: 50%;

    top: 50%;

    transform:
        translate(-18%, -50%);

    display: none;

    align-items: center;

    justify-content: center;

    gap: 9px;

    pointer-events: none;
}

.state-automation .flow-overlay {

    display: flex;

    animation:
        flowAppear 0.8s
        ease-out
        both;
}

.flow-node {

    width: 112px;

    height: 68px;

    border:
        1px solid
        rgba(150, 190, 255, 0.34);

    border-radius: 14px;

    background:
        linear-gradient(
            145deg,
            rgba(26, 45, 82, 0.90),
            rgba(10, 20, 40, 0.78)
        );

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    font-size: 10px;

    letter-spacing: 1.2px;

    text-transform: uppercase;

    box-shadow:
        0 0 25px
        rgba(70, 130, 255, 0.18),

        inset 0 0 20px
        rgba(120, 180, 255, 0.04);

    animation:
        flowNode 1.1s
        ease-in-out
        infinite;
}

.flow-node:nth-child(1) {
    animation-delay: 0s;
}

.flow-node:nth-child(3) {
    animation-delay: 0.15s;
}

.flow-node:nth-child(5) {
    animation-delay: 0.30s;
}

.flow-node:nth-child(7) {
    animation-delay: 0.45s;
}

.flow-arrow {

    font-size: 21px;

    color:
        rgba(130, 190, 255, 0.72);

    animation:
        arrowPulse 0.75s
        ease-in-out
        infinite;
}


/* ============================================================
   DEVICE GRID
   ============================================================ */

.device-grid {

    position: absolute;

    width: 560px;

    height: 280px;

    display: none;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 12px;

    pointer-events: none;

    left: 50%;

    top: 50%;

    transform:
        translate(-50%, -50%);
}

.state-devices .device-grid {

    display: grid;

    animation:
        deviceGridAppear 0.8s
        ease-out
        both;
}

.device-card {

    border:
        1px solid
        rgba(90, 160, 255, 0.22);

    border-radius: 14px;

    background:
        rgba(10, 25, 48, 0.78);

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    gap: 6px;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 1px;

    box-shadow:
        0 0 20px
        rgba(60, 140, 255, 0.08);

    animation:
        deviceCardPulse 1.8s
        ease-in-out
        infinite;
}

.device-card small {

    font-size: 8px;

    color:
        rgba(180, 210, 240, 0.55);

    letter-spacing: 1px;
}

.device-dot {

    width: 8px;

    height: 8px;

    border-radius: 50%;

    background: #54e89a;

    box-shadow:
        0 0 12px
        rgba(84, 232, 154, 0.8);
}

.device-card.unlinked .device-dot {

    background: #8a96a8;

    box-shadow:
        0 0 8px
        rgba(130, 145, 165, 0.4);
}


/* ============================================================
   STATUS
   ============================================================ */

.status {

    margin-top: 24px;

    font-size: 14px;

    letter-spacing: 3px;

    text-transform: uppercase;

    color:
        rgba(210, 225, 245, 0.70);

    min-height: 20px;

    text-align: center;

    transition:
        opacity 0.3s ease;
}


/* ============================================================
   RESPONSE
   ============================================================ */

.response {

    position: absolute;

    bottom: 95px;

    width: min(720px, 82vw);

    padding: 15px 20px;

    border:
        1px solid
        rgba(100, 150, 220, 0.12);

    border-radius: 14px;

    background:
        rgba(7, 15, 28, 0.72);

    backdrop-filter:
        blur(14px);

    color:
        rgba(225, 235, 250, 0.86);

    font-size: 15px;

    line-height: 1.6;

    text-align: center;

    opacity: 0;

    visibility: hidden;

    transform:
        translateY(10px);

    transition:
        opacity 0.3s ease,
        transform 0.3s ease,
        visibility 0.3s ease;

    pointer-events: none;
}

.response.visible {

    opacity: 1;

    visibility: visible;

    transform:
        translateY(0);
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    position: absolute;

    bottom: 28px;

    font-size: 10px;

    letter-spacing: 5px;

    color:
        rgba(160, 180, 210, 0.35);

    text-transform: uppercase;
}


/* ============================================================
   MICROPHONE WARNING
   ============================================================ */

.mic-warning {

    display: none;

    position: absolute;

    bottom: 70px;

    padding: 10px 16px;

    border-radius: 10px;

    background:
        rgba(80, 20, 20, 0.55);

    border:
        1px solid
        rgba(255, 100, 100, 0.2);

    color:
        rgba(255, 190, 190, 0.85);

    font-size: 12px;

    text-align: center;
}


/* ============================================================
   ANIMATIONS
   ============================================================ */

@keyframes breathe {

    0%, 100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.035);
    }
}

@keyframes listeningPulse {

    0%, 100% {
        transform: scale(0.98);
    }

    50% {
        transform: scale(1.06);
    }
}

@keyframes processingMorph {

    0% {
        transform:
            rotate(0deg)
            scale(0.88, 1);
        border-radius:
            44% 56% 51% 49%;
    }

    25% {
        transform:
            rotate(90deg)
            scale(1.18, 0.72);
        border-radius:
            30% 70% 60% 40%;
    }

    50% {
        transform:
            rotate(180deg)
            scale(0.82, 1.18);
        border-radius:
            60% 40% 35% 65%;
    }

    75% {
        transform:
            rotate(270deg)
            scale(1.16, 0.78);
        border-radius:
            25% 75% 65% 35%;
    }

    100% {
        transform:
            rotate(360deg)
            scale(0.88, 1);
        border-radius:
            44% 56% 51% 49%;
    }
}

@keyframes processingWave {

    0% {
        transform:
            rotate(0deg)
            scale(0.75);
        opacity: 0.3;
    }

    50% {
        transform:
            rotate(180deg)
            scale(1.35);
        opacity: 1;
    }

    100% {
        transform:
            rotate(360deg)
            scale(0.75);
        opacity: 0.3;
    }
}

@keyframes processingCore {

    from {
        transform:
            rotate(0deg)
            scale(0.8);
    }

    to {
        transform:
            rotate(360deg)
            scale(1.25);
    }
}

@keyframes processingRing {

    from {
        transform:
            rotate(0deg)
            scale(0.85);
    }

    to {
        transform:
            rotate(360deg)
            scale(1.16);
    }
}

@keyframes voiceRipple {

    0%, 100% {
        transform:
            scale(0.98);
        filter:
            brightness(1);
    }

    25% {
        transform:
            scale(1.05);
    }

    50% {
        transform:
            scale(1.11);
        filter:
            brightness(1.3);
    }

    75% {
        transform:
            scale(1.04);
    }
}

@keyframes speakingRipple {

    0% {
        inset: 10px;
        opacity: 0.6;
    }

    50% {
        inset: -20px;
        opacity: 0.05;
    }

    100% {
        inset: -42px;
        opacity: 0;
    }
}

@keyframes speakingGlow {

    from {
        transform:
            scale(0.85);
        opacity: 0.35;
    }

    to {
        transform:
            scale(1.35);
        opacity: 0.85;
    }
}

@keyframes voiceRing {

    0% {
        transform:
            scale(0.88);
        opacity: 0.35;
    }

    50% {
        transform:
            scale(1.08);
        opacity: 1;
    }

    100% {
        transform:
            scale(1.22);
        opacity: 0.08;
    }
}

@keyframes automationCore {

    0%, 100% {
        transform:
            translateX(-285px)
            rotate(0deg)
            scale(1);
    }

    50% {
        transform:
            translateX(-285px)
            rotate(45deg)
            scale(1.1);
    }
}

@keyframes automationRing {

    from {
        transform:
            translateX(-120px)
            rotate(0deg);
    }

    to {
        transform:
            translateX(-120px)
            rotate(360deg);
    }
}

@keyframes flowAppear {

    from {
        opacity: 0;
        transform:
            translate(-8%, -50%)
            scale(0.7);
    }

    to {
        opacity: 1;
        transform:
            translate(-18%, -50%)
            scale(1);
    }
}

@keyframes flowNode {

    0%, 100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-7px);
    }
}

@keyframes arrowPulse {

    0%, 100% {
        opacity: 0.25;
        transform:
            translateX(-3px);
    }

    50% {
        opacity: 1;
        transform:
            translateX(3px);
    }
}

@keyframes devicePulse {

    0%, 100% {
        transform:
            scale(0.75);
    }

    50% {
        transform:
            scale(0.86);
    }
}

@keyframes deviceGridRotate {

    from {
        transform:
            rotate(0deg);
    }

    to {
        transform:
            rotate(360deg);
    }
}

@keyframes deviceGridAppear {

    from {
        opacity: 0;
        transform:
            translate(-50%, -50%)
            scale(0.72);
    }

    to {
        opacity: 1;
        transform:
            translate(-50%, -50%)
            scale(1);
    }
}

@keyframes deviceCardPulse {

    0%, 100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-4px);
    }
}

@keyframes rotate {

    from {
        transform:
            rotate(0deg);
    }

    to {
        transform:
            rotate(360deg);
    }
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    .orb-container {
        transform: scale(0.78);
    }

    .state-automation .orb-container,
    .state-devices .orb-container {
        transform: scale(0.50);
    }

    .top-label {
        left: 18px;
    }

    .system-status {
        right: 18px;
    }

    .footer {
        letter-spacing: 3px;
    }
}

</style>

</head>


<body>

<div id="app">

    <div class="top-label">
        STERLING
    </div>


    <div
        class="system-status"
        id="systemStatus"
    >
        SYSTEM ONLINE
    </div>


    <div class="orb-container">

        <div class="orb-ring"></div>

        <div class="orb-ring"></div>

        <div class="orb-ring"></div>


        <div
            class="orb"
            id="orb"
        ></div>


        <!-- ==================================================
             AUTOMATION VISUAL
             ================================================== -->

        <div
            class="flow-overlay"
            id="flowOverlay"
        >

            <div class="flow-node">
                VOICE INPUT
            </div>

            <div class="flow-arrow">
                →
            </div>

            <div class="flow-node">
                STERLING
            </div>

            <div class="flow-arrow">
                →
            </div>

            <div class="flow-node">
                LOGIC
            </div>

            <div class="flow-arrow">
                →
            </div>

            <div class="flow-node">
                ACTION
            </div>

        </div>


        <!-- ==================================================
             DEVICE VISUAL
             ================================================== -->

        <div
            class="device-grid"
            id="deviceGrid"
        >

            <div class="device-card">

                <div class="device-dot"></div>

                COMMAND TOWER

                <small>
                    ONLINE
                </small>

            </div>


            <div class="device-card unlinked">

                <div class="device-dot"></div>

                PHONE

                <small>
                    NOT LINKED
                </small>

            </div>


            <div class="device-card unlinked">

                <div class="device-dot"></div>

                SAMSUNG TV

                <small>
                    NOT LINKED
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                AI ENGINE

                <small>
                    READY
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                AUTOMATION

                <small>
                    READY
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                LOCAL NETWORK

                <small>
                    AVAILABLE
                </small>

            </div>

        </div>

    </div>


    <div
        class="status"
        id="status"
    >
        STANDBY — SAY STERLING
    </div>


    <!--
        Hidden by default.

        STERLING remembers and speaks the response.

        This only becomes visible when explicitly requested.
    -->

    <div
        class="response"
        id="response"
    ></div>


    <div
        class="mic-warning"
        id="micWarning"
    >
        Microphone access is required for voice interaction.
        Please allow microphone access in your browser.
    </div>


    <div class="footer">
        STERLING COMMAND TOWER
    </div>

</div>


<script>


// ============================================================
// STATE
// ============================================================

let recognition = null;

let wakeRecognition = null;

let isProcessing = false;

let isSpeaking = false;

let wakeRestartTimer = null;

let lastResponse = "";

let responseVisible = false;


// ============================================================
// ELEMENTS
// ============================================================

const app =
    document.getElementById("app");

const statusElement =
    document.getElementById("status");

const responseElement =
    document.getElementById("response");

const systemStatus =
    document.getElementById("systemStatus");

const micWarning =
    document.getElementById("micWarning");


// ============================================================
// STATE MANAGEMENT
// ============================================================

function setState(state, text) {

    app.classList.remove(
        "state-listening",
        "state-processing",
        "state-speaking",
        "state-automation",
        "state-devices"
    );


    if (state === "listening") {

        app.classList.add(
            "state-listening"
        );
    }


    if (state === "processing") {

        app.classList.add(
            "state-processing"
        );
    }


    if (state === "speaking") {

        app.classList.add(
            "state-speaking"
        );
    }


    if (state === "automation") {

        app.classList.add(
            "state-automation"
        );
    }


    if (state === "devices") {

        app.classList.add(
            "state-devices"
        );
    }


    statusElement.textContent =
        text;
}


// ============================================================
// RESPONSE MEMORY
// ============================================================

function rememberResponse(text) {

    lastResponse =
        text || "";
}


function showResponse(text) {

    rememberResponse(text);

    responseElement.textContent =
        text;

    responseElement.classList.add(
        "visible"
    );

    responseVisible = true;
}


function hideResponse() {

    responseElement.classList.remove(
        "visible"
    );

    responseVisible = false;
}


function toggleResponse() {

    if (!lastResponse) {

        return;
    }

    if (responseVisible) {

        hideResponse();

    } else {

        showResponse(
            lastResponse
        );
    }
}


// ============================================================
// SPEECH RECOGNITION
// ============================================================

function getSpeechRecognition() {

    return (
        window.SpeechRecognition ||
        window.webkitSpeechRecognition ||
        null
    );
}


function createRecognition() {

    const Recognition =
        getSpeechRecognition();

    if (!Recognition) {

        return null;
    }

    const instance =
        new Recognition();

    instance.lang =
        "en-US";

    instance.continuous =
        false;

    instance.interimResults =
        false;

    instance.maxAlternatives =
        1;

    return instance;
}


// ============================================================
// COMMAND CLEANING
// ============================================================

function cleanCommand(text) {

    if (!text) {

        return "";
    }

    return text
        .trim()
        .replace(
            /^\s*sterling[\s,:-]*/i,
            ""
        )
        .trim();
}


function extractAfterWakeWord(text) {

    if (!text) {

        return "";
    }

    const match =
        text.match(
            /\bsterling\b(.*)/i
        );

    if (!match) {

        return "";
    }

    return match[1]
        .replace(
            /^[\s,:-]+/,
            ""
        )
        .trim();
}


// ============================================================
// TIME-AWARE GREETING
// ============================================================

function getLocalGreeting() {

    const hour =
        new Date().getHours();

    if (hour >= 5 && hour < 12) {

        return "Good morning, sir.";
    }

    if (hour >= 12 && hour < 18) {

        return "Good afternoon, sir.";
    }

    if (hour >= 18 && hour < 22) {

        return "Good evening, sir.";
    }

    return "Good night, sir.";
}


// ============================================================
// WAKE LISTENER
// ============================================================

function stopWakeListener() {

    if (wakeRestartTimer) {

        clearTimeout(
            wakeRestartTimer
        );

        wakeRestartTimer =
            null;
    }


    if (wakeRecognition) {

        try {

            wakeRecognition.onend =
                null;

            wakeRecognition.stop();

        } catch (error) {}

        wakeRecognition =
            null;
    }
}


function scheduleWakeRestart() {

    if (wakeRestartTimer) {

        return;
    }

    wakeRestartTimer =
        setTimeout(
            function() {

                wakeRestartTimer =
                    null;

                if (
                    !isProcessing &&
                    !isSpeaking
                ) {

                    startWakeListener();
                }

            },
            700
        );
}


function startWakeListener() {

    if (
        isProcessing ||
        isSpeaking
    ) {

        return;
    }


    stopWakeListener();


    wakeRecognition =
        createRecognition();


    if (!wakeRecognition) {

        systemStatus.textContent =
            "VOICE UNSUPPORTED";

        statusElement.textContent =
            "USE CHROME OR EDGE";

        micWarning.style.display =
            "block";

        return;
    }


    wakeRecognition.onstart =
        function() {

            systemStatus.textContent =
                "LISTENING FOR WAKE WORD";

            setState(
                "standby",
                "STANDBY — SAY STERLING"
            );
        };


    wakeRecognition.onresult =
        function(event) {

            const result =
                event.results[
                    event.results.length - 1
                ];


            if (
                !result ||
                !result[0]
            ) {

                return;
            }


            const transcript =
                result[0]
                    .transcript
                    .trim();


            if (
                !transcript
                    .toLowerCase()
                    .includes("sterling")
            ) {

                return;
            }


            stopWakeListener();


            const command =
                extractAfterWakeWord(
                    transcript
                );


            activateSterling(
                command
            );
        };


    wakeRecognition.onerror =
        function(event) {

            if (
                event.error ===
                    "not-allowed" ||
                event.error ===
                    "service-not-allowed"
            ) {

                systemStatus.textContent =
                    "MICROPHONE BLOCKED";

                statusElement.textContent =
                    "ALLOW MICROPHONE ACCESS";

                micWarning.style.display =
                    "block";

                return;
            }


            scheduleWakeRestart();
        };


    wakeRecognition.onend =
        function() {

            if (
                !isProcessing &&
                !isSpeaking
            ) {

                scheduleWakeRestart();
            }
        };


    try {

        wakeRecognition.start();

    } catch (error) {

        scheduleWakeRestart();
    }
}


// ============================================================
// WAKE ACTIVATION
// ============================================================

function activateSterling(command = "") {

    stopWakeListener();


    const greeting =
        getLocalGreeting();


    setState(
        "speaking",
        "STERLING ONLINE"
    );


    speak(
        greeting +
        " How may I assist you?",
        function() {

            if (command) {

                sendCommand(
                    command
                );

            } else {

                startCommandListener();
            }

        }
    );
}


// ============================================================
// COMMAND LISTENER
// ============================================================

function startCommandListener() {

    stopWakeListener();


    recognition =
        createRecognition();


    if (!recognition) {

        statusElement.textContent =
            "VOICE UNSUPPORTED";

        return;
    }


    setState(
        "listening",
        "LISTENING"
    );


    recognition.onresult =
        function(event) {

            const result =
                event.results[
                    event.results.length - 1
                ];


            if (
                !result ||
                !result[0]
            ) {

                return;
            }


            const transcript =
                result[0]
                    .transcript
                    .trim();


            const command =
                cleanCommand(
                    transcript
                );


            if (!command) {

                returnToStandby();

                return;
            }


            try {

                recognition.stop();

            } catch (error) {}


            sendCommand(
                command
            );
        };


    recognition.onerror =
        function(event) {

            if (
                event.error ===
                    "not-allowed" ||
                event.error ===
                    "service-not-allowed"
            ) {

                micWarning.style.display =
                    "block";

                statusElement.textContent =
                    "ALLOW MICROPHONE ACCESS";

                return;
            }


            returnToStandby();
        };


    recognition.onend =
        function() {

            if (
                !isProcessing &&
                !isSpeaking &&
                statusElement.textContent ===
                    "LISTENING"
            ) {

                returnToStandby();
            }
        };


    try {

        recognition.start();

    } catch (error) {

        returnToStandby();
    }
}


// ============================================================
// SPECIAL LOCAL COMMANDS
// ============================================================

function handleLocalCommand(command) {

    const text =
        command.toLowerCase().trim();


    // --------------------------------------------------------
    // SHOW LAST RESPONSE
    // --------------------------------------------------------

    if (
        text.includes("show response") ||
        text.includes("show the response") ||
        text.includes("show me the response") ||
        text.includes("display response") ||
        text.includes("display the response") ||
        text.includes("show what you said") ||
        text.includes("show me what you said") ||
        text.includes("what did you just say") ||
        text.includes("show your last response") ||
        text.includes("show me your last response")
    ) {

        showResponse(
            lastResponse ||
            "There is no response currently stored."
        );

        speak(
            "Displaying my last response, sir.",
            function() {

                returnToStandby();

            }
        );

        return true;
    }


    // --------------------------------------------------------
    // HIDE RESPONSE
    // --------------------------------------------------------

    if (
        text.includes("hide response") ||
        text.includes("hide the response") ||
        text.includes("hide that")
    ) {

        hideResponse();

        speak(
            "Response display hidden, sir.",
            function() {

                returnToStandby();

            }
        );

        return true;
    }


    // --------------------------------------------------------
    // AUTOMATION VISUAL
    // --------------------------------------------------------

    if (
        text.includes("show automation") ||
        text.includes("show the automation") ||
        text.includes("show workflow") ||
        text.includes("show the workflow") ||
        text.includes("show logic chain") ||
        text.includes("show the logic chain") ||
        text.includes("show the flow")
    ) {

        setState(
            "automation",
            "AUTOMATION FLOW"
        );

        speak(
            "Displaying the automation flow, sir.",
            function() {

                setTimeout(
                    returnToStandby,
                    6000
                );

            }
        );

        return true;
    }


    // --------------------------------------------------------
    // DEVICE VISUAL
    // --------------------------------------------------------

    if (
        text.includes("show devices") ||
        text.includes("show the devices") ||
        text.includes("show connected devices") ||
        text.includes("show my devices") ||
        text.includes("device status") ||
        text.includes("show hardware")
    ) {

        setState(
            "devices",
            "DEVICE STATUS MAP"
        );

        speak(
            "Displaying the device status map, sir.",
            function() {

                setTimeout(
                    returnToStandby,
                    6000
                );

            }
        );

        return true;
    }


    return false;
}


// ============================================================
// SEND COMMAND
// ============================================================

async function sendCommand(command) {

    if (
        !command ||
        isProcessing ||
        isSpeaking
    ) {

        return;
    }


    // Local visual/interface commands.
    if (
        handleLocalCommand(
            command
        )
    ) {

        return;
    }


    isProcessing =
        true;


    stopWakeListener();


    if (recognition) {

        try {

            recognition.stop();

        } catch (error) {}

        recognition =
            null;
    }


    hideResponse();


    // --------------------------------------------------------
    // PROCESSING VISUAL
    // --------------------------------------------------------

    setState(
        "processing",
        "PROCESSING"
    );


    systemStatus.textContent =
        "STERLING IS THINKING";


    try {

        const url =
            "/api/chat?prompt=" +
            encodeURIComponent(
                command
            );


        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                "Server returned " +
                response.status
            );
        }


        const data =
            await response.json();


        const answer =
            data.sterling_response ||
            data.response ||
            data.message ||
            "I was unable to formulate a response.";


        const visualMode =
            data.visual_mode ||
            "processing";


        const showText =
            Boolean(
                data.show_text
            );


        rememberResponse(
            answer
        );


        // Only display if the backend explicitly
        // says the user requested the text.
        if (showText) {

            showResponse(
                answer
            );

        } else {

            hideResponse();
        }


        // ----------------------------------------------------
        // MORPH INTO VISUAL MODE
        // ----------------------------------------------------

        if (
            visualMode ===
            "automation"
        ) {

            setState(
                "automation",
                "AUTOMATION FLOW"
            );

        } else if (
            visualMode ===
            "devices"
        ) {

            setState(
                "devices",
                "DEVICE STATUS MAP"
            );

        } else {

            setState(
                "processing",
                "PROCESSING"
            );
        }


        isProcessing =
            false;


        // ----------------------------------------------------
        // SPEAK
        // ----------------------------------------------------

        speak(
            answer,
            function() {

                /*
                    The orb returns to standby only
                    after STERLING finishes speaking.
                */

                returnToStandby();

            }
        );


    } catch (error) {

        console.error(error);


        const message =
            "I encountered a connection problem.";


        rememberResponse(
            message
        );


        isProcessing =
            false;


        speak(
            message,
            function() {

                returnToStandby();

            }
        );
    }
}


// ============================================================
// MALE VOICE SELECTION
// ============================================================

function findMaleVoice(voices) {

    if (
        !voices ||
        !voices.length
    ) {

        return null;
    }


    /*
        Strongly preferred male voices.

        Exact availability depends on the operating system
        and browser.
    */

    const preferredMaleNames = [

        "Microsoft Guy",

        "Microsoft Ryan",

        "Microsoft Christopher",

        "Microsoft David",

        "Microsoft Mark",

        "Microsoft Eric",

        "Microsoft George",

        "Microsoft James",

        "Microsoft Brian",

        "Microsoft Daniel",

        "Google UK English Male",

        "Google US English Male",

        "Alex",

        "Daniel"

    ];


    for (
        const preferred
        of preferredMaleNames
    ) {

        const match =
            voices.find(
                function(voice) {

                    return voice.name
                        .toLowerCase()
                        .includes(
                            preferred
                                .toLowerCase()
                        );
                }
            );


        if (match) {

            return match;
        }
    }


    /*
        Second pass:
        look for strong male indicators.
    */

    const maleIndicators = [

        "male",

        "guy",

        "david",

        "ryan",

        "daniel",

        "christopher",

        "george",

        "james",

        "mark",

        "brian",

        "alex",

        "fred",

        "arthur",

        "oliver",

        "thomas"

    ];


    for (
        const voice
        of voices
    ) {

        const name =
            voice.name.toLowerCase();


        const language =
            voice.lang.toLowerCase();


        if (
            !language.startsWith("en")
        ) {

            continue;
        }


        for (
            const indicator
            of maleIndicators
        ) {

            if (
                name.includes(
                    indicator
                )
            ) {

                return voice;
            }
        }
    }


    /*
        Explicitly avoid common female voice names
        before choosing an English fallback.
    */

    const femaleIndicators = [

        "samantha",

        "zira",

        "susan",

        "female",

        "karen",

        "moira",

        "victoria",

        "hazel",

        "sara",

        "sarah",

        "aria",

        "jenny",

        "libby",

        "siri",

        "ava",

        "allison",

        "joanna",

        "kate",

        "serena",

        "fiona",

        "emily",

        "lucy",

        "google us english"

    ];


    const safeEnglishVoices =
        voices.filter(
            function(voice) {

                const name =
                    voice.name
                        .toLowerCase();

                const language =
                    voice.lang
                        .toLowerCase();


                const isFemale =
                    femaleIndicators.some(
                        function(indicator) {

                            return name.includes(
                                indicator
                            );
                        }
                    );


                return (
                    !isFemale &&
                    language.startsWith("en")
                );
            }
        );


    if (
        safeEnglishVoices.length
    ) {

        return safeEnglishVoices[0];
    }


    return null;
}


// ============================================================
// SPEECH
// ============================================================

function speak(
    text,
    onComplete
) {

    if (
        !("speechSynthesis" in window)
    ) {

        if (onComplete) {

            onComplete();
        }

        return;
    }


    isSpeaking =
        true;


    stopWakeListener();


    window.speechSynthesis.cancel();


    const utterance =
        new SpeechSynthesisUtterance(
            text
        );


    utterance.lang =
        "en-US";


    /*
        Slightly slower, deeper delivery for
        the digital-butler character.
    */

    utterance.rate =
        0.92;


    utterance.pitch =
        0.78;


    utterance.volume =
        1.0;


    const voices =
        window.speechSynthesis
            .getVoices();


    const selectedVoice =
        findMaleVoice(
            voices
        );


    if (selectedVoice) {

        utterance.voice =
            selectedVoice;

        console.log(
            "STERLING voice:",
            selectedVoice.name
        );
    }


    utterance.onstart =
        function() {

            setState(
                "speaking",
                "SPEAKING"
            );

            systemStatus.textContent =
                "STERLING SPEAKING";
        };


    utterance.onend =
        function() {

            isSpeaking =
                false;


            if (onComplete) {

                onComplete();
            }
        };


    utterance.onerror =
        function() {

            isSpeaking =
                false;


            if (onComplete) {

                onComplete();
            }
        };


    window.speechSynthesis.speak(
        utterance
    );
}


// ============================================================
// RETURN TO STANDBY
// ============================================================

function returnToStandby() {

    isProcessing =
        false;

    isSpeaking =
        false;


    systemStatus.textContent =
        "SYSTEM ONLINE";


    setState(
        "standby",
        "STANDBY — SAY STERLING"
    );


    setTimeout(
        function() {

            if (
                !isProcessing &&
                !isSpeaking
            ) {

                startWakeListener();
            }

        },
        900
    );
}


// ============================================================
// INITIALISE
// ============================================================

function initialiseSterling() {

    if (
        !getSpeechRecognition()
    ) {

        systemStatus.textContent =
            "VOICE UNSUPPORTED";

        statusElement.textContent =
            "USE CHROME OR EDGE";

        micWarning.style.display =
            "block";

        return;
    }


    if (
        "speechSynthesis"
        in window
    ) {

        window.speechSynthesis
            .getVoices();


        window.speechSynthesis
            .onvoiceschanged =
            function() {

                const voices =
                    window.speechSynthesis
                        .getVoices();

                const maleVoice =
                    findMaleVoice(
                        voices
                    );

                if (maleVoice) {

                    console.log(
                        "STERLING male voice ready:",
                        maleVoice.name
                    );
                }

            };
    }


    setTimeout(
        function() {

            startWakeListener();

        },
        1000
    );
}


window.addEventListener(
    "load",
    initialiseSterling
);


</script>

</body>

</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home():

    return HTMLResponse(
        content=ORB_UI_HTML
    )


# ============================================================
# CHAT API
# ============================================================

@app.get("/api/chat")
async def chat(
    prompt: str = Query(
        ...,
        min_length=1,
    )
):

    response, visual_mode, show_text = \
        generate_response(
            prompt
        )

    return {

        "sterling_response":
            response,

        "visual_mode":
            visual_mode,

        "show_text":
            show_text,

        "system":
            "STERLING",

        "designation":
            STERLING_ACRONYM,

        "creator":
            CREATOR_NAME,
    }


# ============================================================
# STATUS
# ============================================================

@app.get("/api/status")
async def status():

    return {

        "status":
            "online",

        "system":
            "STERLING",

        "designation":
            STERLING_ACRONYM,

        "creator":
            CREATOR_NAME,

        "groq_configured":
            bool(GROQ_API_KEY),

        "gemini_configured":
            bool(GEMINI_API_KEY),

        "gemini_model":
            GEMINI_MODEL,

        "conversation_memory":
            len(conversation_history),

        "last_response_stored":
            bool(last_response_memory),
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {

        "status":
            "healthy",

        "system":
            "STERLING",

        "version":
            "3.0.0",

    }


# ============================================================
# WEBSOCKET
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            data = await websocket.receive_text()


            response, visual_mode, show_text = \
                generate_response(
                    data
                )


            await websocket.send_json({

                "sterling_response":
                    response,

                "visual_mode":
                    visual_mode,

                "show_text":
                    show_text,

                "system":
                    "STERLING",

                "creator":
                    CREATOR_NAME,

            })


    except Exception as error:

        print(
            "WebSocket closed:",
            error
        )
