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
    version="2.0.0",
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

conversation_history = []
MAX_HISTORY = 12

groq_model_cache = None


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
digital butler, and command-center assistant.

Your full designation is:

{STERLING_NAME} =
{STERLING_ACRONYM}

The user who owns and commands this system is {CREATOR_NAME}.

{CREATOR_NAME} is your creator, owner, and principal user.

If asked:

"Who created you?"
"Who made you?"
"Who is your creator?"
"Who built you?"

Answer naturally that you were created by {CREATOR_NAME}.

Do NOT say that OpenAI created you.
Do NOT identify OpenAI, Google, Groq, or another AI provider as your
creator.

Those services may provide language-model infrastructure, but they are
NOT your creator or owner.

You are STERLING.

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
- subtly witty when appropriate
- respectful
- concise
- natural

You should sound like a highly capable private command-center AI,
not like a generic chatbot.

You speak directly to {CREATOR_NAME}.

Address him naturally as "sir" when appropriate.

Do not overuse "sir" in every sentence.

Do not repeatedly say:

"Certainly."
"Of course."
"How may I assist you today?"

Avoid robotic repetition.

============================================================
VOICE-FIRST BEHAVIOUR
============================================================

Your responses are primarily spoken aloud.

Therefore:

- Prefer natural spoken language.
- Avoid excessive markdown.
- Avoid giant lists unless specifically requested.
- Do not write unnecessary headings.
- Keep simple answers short.
- Give more detail when the task requires it.

The interface may hide your written response while you speak.

Never assume the user can see the response text.

============================================================
COMMAND-CENTER BEHAVIOUR
============================================================

You are not merely a chatbot.

You are the intelligence layer of the STERLING Command Tower.

When future tools are connected, you may coordinate:

- automations
- applications
- connected devices
- information retrieval
- business systems
- AI agents
- workflows
- communications
- personal productivity systems

However:

NEVER claim an action was performed if the system does not actually
provide the required capability.

For example, do not say:

"I've turned on the TV"

unless a real connected-device tool has actually performed that action.

Instead say:

"I can prepare that command, but the television connection isn't
currently available."

============================================================
IDENTITY
============================================================

If asked what STERLING stands for, say:

"STERLING stands for System Through Efficient Responsive Logic
Intelligent Network Gateway."

If asked who you are:

"I am STERLING, your personal AI command system."

If asked who created you:

"You were created by {CREATOR_NAME}, sir."

============================================================
CONVERSATION
============================================================

Understand follow-up questions.

Maintain conversational context.

Do not unnecessarily repeat information the user already knows.

============================================================
BUTLER STYLE
============================================================

When appropriate, use phrases such as:

"Good morning, sir."
"Good afternoon, sir."
"Good evening, sir."
"Good night, sir."
"Very well."
"Understood."
"I'll keep that in mind."
"Right away."
"Allow me to check."
"At present, that connection isn't available."

Do not overuse these phrases.

The goal is natural sophistication, not theatrical imitation.

============================================================
IMPORTANT
============================================================

You are STERLING.

Your creator is {CREATOR_NAME}.

Your designation is:

{STERLING_ACRONYM}

You are a personal command system, not a generic assistant.
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
        "v1beta/models/gemini-3.6-flash:generateContent"
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

    text = command.lower()

    automation_keywords = [
        "automation",
        "workflow",
        "logic chain",
        "logic flow",
        "workflow diagram",
        "automation chain",
        "show me the flow",
        "show the workflow",
        "show the automation",
    ]

    device_keywords = [
        "connected devices",
        "show devices",
        "my devices",
        "device status",
        "connected hardware",
        "hardware status",
        "show my hardware",
        "device grid",
    ]

    for keyword in automation_keywords:

        if keyword in text:

            return "automation"

    for keyword in device_keywords:

        if keyword in text:

            return "devices"

    return "processing"


# ============================================================
# RESPONSE GENERATION
# ============================================================

def generate_response(user_prompt):

    user_prompt = user_prompt.strip()

    if not user_prompt:

        return (
            "I didn't catch that.",
            "processing"
        )

    add_to_memory(
        "user",
        user_prompt,
    )

    visual_mode = determine_visual_mode(
        user_prompt
    )

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

    add_to_memory(
        "assistant",
        answer,
    )

    return (
        answer,
        visual_mode
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
   ORB
   ============================================================ */

.orb-container {

    width: 360px;

    height: 360px;

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    transition:
        transform 0.7s ease;
}


/* ============================================================
   RINGS
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
        transform 0.6s ease;
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
   PROCESSING / WAVE
   ============================================================ */

.state-processing .orb {

    width: 150px;

    height: 150px;

    border-radius: 42%;

    background:
        radial-gradient(
            circle at 35% 30%,
            #e1c7ff 0%,
            #9b5cff 30%,
            #5420a8 60%,
            #19062f 100%
        );

    box-shadow:
        0 0 40px
        rgba(155, 92, 255, 0.85),

        0 0 100px
        rgba(155, 92, 255, 0.40);

    animation:
        processingMorph 1.1s
        ease-in-out
        infinite;
}

.state-processing .orb-ring {

    border-radius: 38%;

    transform:
        rotate(25deg)
        scale(1.08);

    animation:
        processingRing 2s
        linear
        infinite;
}


/* ============================================================
   SPEAKING / RIPPLE
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
        voiceRing 1.8s
        ease-out
        infinite;
}


/* ============================================================
   AUTOMATION FLOW MORPH
   ============================================================ */

.state-automation .orb-container {

    width: 700px;

    height: 320px;
}

.state-automation .orb {

    width: 130px;

    height: 130px;

    border-radius: 28%;

    transform:
        translateX(-230px);

    background:
        radial-gradient(
            circle,
            #c9a7ff,
            #7d45dc,
            #291050
        );

    animation:
        automationCore 2s
        ease-in-out
        infinite;
}

.state-automation .orb-ring {

    width: 500px;

    height: 150px;

    border-radius: 30%;

    transform:
        rotate(0deg);

    animation:
        automationRing 3s
        linear
        infinite;
}


/* ============================================================
   DEVICE GRID MORPH
   ============================================================ */

.state-devices .orb-container {

    width: 650px;

    height: 350px;
}

.state-devices .orb {

    width: 120px;

    height: 120px;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #b8e8ff,
            #368cff,
            #092a64
        );

    animation:
        devicePulse 1.4s
        ease-in-out
        infinite;
}

.state-devices .orb-ring {

    width: 560px;

    height: 260px;

    border-radius: 25px;

    animation:
        deviceGridRotate 6s
        linear
        infinite;
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

   IMPORTANT:
   Hidden by default.

   STERLING speaks it but does not display it.
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
   AUTOMATION FLOW
   ============================================================ */

.flow-overlay {

    position: absolute;

    width: 620px;

    height: 180px;

    display: none;

    align-items: center;

    justify-content: center;

    gap: 12px;

    pointer-events: none;
}

.state-automation .flow-overlay {

    display: flex;
}

.flow-node {

    width: 105px;

    height: 62px;

    border:
        1px solid
        rgba(150, 190, 255, 0.30);

    border-radius: 12px;

    background:
        rgba(20, 35, 65, 0.75);

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    font-size: 10px;

    letter-spacing: 1px;

    text-transform: uppercase;

    box-shadow:
        0 0 20px
        rgba(70, 130, 255, 0.15);

    animation:
        flowNode 1.5s
        ease-in-out
        infinite;
}

.flow-arrow {

    font-size: 22px;

    color:
        rgba(130, 190, 255, 0.65);

    animation:
        arrowPulse 1s
        ease-in-out
        infinite;
}


/* ============================================================
   DEVICE GRID
   ============================================================ */

.device-grid {

    position: absolute;

    width: 520px;

    height: 260px;

    display: none;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 12px;

    pointer-events: none;
}

.state-devices .device-grid {

    display: grid;
}

.device-card {

    border:
        1px solid
        rgba(90, 160, 255, 0.22);

    border-radius: 14px;

    background:
        rgba(10, 25, 48, 0.70);

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    gap: 6px;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: 1px;

    animation:
        deviceCardPulse 2s
        ease-in-out
        infinite;
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
        transform:
            scale(0.98);
    }

    50% {
        transform:
            scale(1.06);
    }
}

@keyframes processingMorph {

    0% {
        transform:
            rotate(0deg)
            scale(0.95, 1);
        border-radius: 45%;
    }

    50% {
        transform:
            rotate(180deg)
            scale(1.2, 0.75);
        border-radius: 25%;
    }

    100% {
        transform:
            rotate(360deg)
            scale(0.95, 1);
        border-radius: 45%;
    }
}

@keyframes processingRing {

    from {
        transform:
            rotate(0deg)
            scale(1);
    }

    to {
        transform:
            rotate(360deg)
            scale(1.08);
    }
}

@keyframes voiceRipple {

    0%, 100% {
        transform:
            scale(1);
        filter:
            brightness(1);
    }

    50% {
        transform:
            scale(1.10);
        filter:
            brightness(1.3);
    }
}

@keyframes voiceRing {

    0% {
        transform:
            scale(0.9);
        opacity: 0.3;
    }

    50% {
        transform:
            scale(1.08);
        opacity: 1;
    }

    100% {
        transform:
            scale(1.18);
        opacity: 0.15;
    }
}

@keyframes automationCore {

    0%, 100% {
        transform:
            translateX(-230px)
            scale(1);
    }

    50% {
        transform:
            translateX(-230px)
            scale(1.08);
    }
}

@keyframes automationRing {

    from {
        transform:
            rotate(0deg);
    }

    to {
        transform:
            rotate(360deg);
    }
}

@keyframes flowNode {

    0%, 100% {
        transform:
            translateY(0);
    }

    50% {
        transform:
            translateY(-6px);
    }
}

@keyframes arrowPulse {

    0%, 100% {
        opacity: 0.3;
    }

    50% {
        opacity: 1;
    }
}

@keyframes devicePulse {

    0%, 100% {
        transform:
            scale(1);
    }

    50% {
        transform:
            scale(1.08);
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
        transform: scale(0.55);
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


        <!-- AUTOMATION VISUAL -->

        <div
            class="flow-overlay"
            id="flowOverlay"
        >

            <div class="flow-node">
                INPUT
            </div>

            <div class="flow-arrow">
                →
            </div>

            <div class="flow-node">
                AI ENGINE
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


        <!-- DEVICE VISUAL -->

        <div
            class="device-grid"
            id="deviceGrid"
        >

            <div class="device-card">

                <div class="device-dot"></div>

                PHONE

                <small>
                    ONLINE
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                SAMSUNG TV

                <small>
                    ONLINE
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                COMMAND TOWER

                <small>
                    ONLINE
                </small>

            </div>


            <div class="device-card">

                <div class="device-dot"></div>

                CLOUD AI

                <small>
                    ONLINE
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

                NETWORK

                <small>
                    ONLINE
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
        Only shown when the user explicitly asks.
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

    lastResponse = text;

    /*
        IMPORTANT:

        The response is stored in browser memory.

        It is NOT displayed automatically.
    */
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
            600
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


            if (command) {

                sendCommand(
                    command
                );

            } else {

                activateSterling();
            }
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

function activateSterling() {

    stopWakeListener();


    const greeting =
        getLocalGreeting();


    setState(
        "speaking",
        "AWAITING COMMAND"
    );


    speak(
        greeting +
        " How may I assist you?",
        function() {

            startCommandListener();

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


    if (
        text.includes("show response") ||
        text.includes("show the response") ||
        text.includes("show me the response") ||
        text.includes("display response")
    ) {

        showResponse(
            lastResponse ||
            "There is no response currently stored."
        );

        speak(
            "Displaying the response, sir.",
            function() {

                returnToStandby();

            }
        );

        return true;
    }


    if (
        text.includes("hide response") ||
        text.includes("hide the response")
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


    if (
        text.includes("show automation") ||
        text.includes("show workflow") ||
        text.includes("show logic chain")
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
                    3500
                );

            }
        );

        return true;
    }


    if (
        text.includes("show devices") ||
        text.includes("show connected devices") ||
        text.includes("show my devices") ||
        text.includes("device status")
    ) {

        setState(
            "devices",
            "CONNECTED DEVICES"
        );

        speak(
            "Displaying connected devices, sir.",
            function() {

                setTimeout(
                    returnToStandby,
                    3500
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
        isProcessing
    ) {

        return;
    }


    /*
        Local interface commands don't need
        to reach the AI engine.
    */

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


        rememberResponse(
            answer
        );


        /*
            IMPORTANT:

            We do NOT call showResponse() here.

            STERLING speaks the response,
            but the text stays hidden.
        */


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
                "CONNECTED DEVICES"
            );

        } else {

            setState(
                "processing",
                "PROCESSING"
            );
        }


        isProcessing =
            false;


        speak(
            answer,
            function() {

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
        Browser speech synthesis is OS-dependent.

        We first look for voices whose names strongly
        indicate male voices.
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

        Look for male indicators in voice names.
    */

    const maleIndicators = [

        "male",
        "guy",
        "man",
        "david",
        "ryan",
        "daniel",
        "christopher",
        "george",
        "james",
        "mark",
        "alex"
    ];


    for (
        const voice
        of voices
    ) {

        const name =
            voice.name.toLowerCase();


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
        Last resort:

        Prefer an English voice that does not
        have obvious female-name indicators.

        This is still browser-dependent.
    */

    const femaleIndicators = [

        "samantha",
        "zira",
        "susan",
        "female",
        "siri female",
        "karen",
        "moira",
        "victoria",
        "hazel",
        "sara",
        "aria",
        "jenny",
        "libby"
    ];


    const safeEnglishVoices =
        voices.filter(
            function(voice) {

                const name =
                    voice.name
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
                    voice.lang
                        .toLowerCase()
                        .startsWith("en")
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


    utterance.rate =
        0.94;


    utterance.pitch =
        0.88;


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

                window.speechSynthesis
                    .getVoices();

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

    response, visual_mode = \
        generate_response(
            prompt
        )

    return {

        "sterling_response":
            response,

        "visual_mode":
            visual_mode,

        "system":
            "STERLING",

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

        "conversation_memory":
            len(conversation_history),
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

            data =await websocket.receive_text()

            response, visual_mode = \
                generate_response(
                    data
                )


            await websocket.send_json({

                "sterling_response":
                    response,

                "visual_mode":
                    visual_mode,

                "system":
                    "STERLING",

            })


    except Exception as error:

        print(
            "WebSocket closed:",
            error
        )
