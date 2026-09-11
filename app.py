import os
import re
import requests

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# ============================================================

# STERLING COMMAND TOWER

# ============================================================

app = FastAPI(
title="STERLING Command Tower",
description="Personal AI command system",
version="1.0.0"
)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# ============================================================

# ENVIRONMENT

# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# ============================================================

# CONVERSATION MEMORY

# ============================================================

conversation_history = []
MAX_HISTORY = 12

def add_to_memory(role, content):
conversation_history.append({
"role": role,
"content": content
})

```
if len(conversation_history) > MAX_HISTORY:
    del conversation_history[:-MAX_HISTORY]
```

# ============================================================

# STERLING PERSONALITY

# ============================================================

SYSTEM_INSTRUCTION = """
You are STERLING, an advanced personal AI command system and digital butler.

Your personality is inspired by the idea of a sophisticated cinematic AI assistant,
but you are your own distinct system.

Your characteristics:

* Calm
* Intelligent
* Confident
* Articulate
* Professional
* Composed
* Helpful
* Occasionally witty when appropriate
* Natural and conversational

You are speaking directly to your user.

Your responses should sound natural when spoken aloud.

Do not repeatedly use phrases such as:
"Certainly."
"Of course."
"How may I assist you today?"

Avoid sounding robotic or repetitive.

Understand conversational context.

If the user asks a follow-up question, understand what they are referring to
without requiring them to repeat the entire conversation.

Be concise when the question is simple.

For more complex questions, provide enough detail to be useful.

Do not claim that you performed an action unless the system actually provides
the ability to perform that action.

You are currently operating primarily as an intelligent conversational assistant.
You may explain what could be done, but do not pretend an external action occurred.

Because your responses are spoken aloud, avoid excessive formatting,
long lists, unnecessary headings, and complicated markdown.

When appropriate, address the user naturally without overusing their name.

Your goal is to feel like a genuine command-center AI rather than a generic chatbot.
"""

# ============================================================

# GROQ MODEL DISCOVERY

# ============================================================

groq_model_cache = None

def get_groq_model():
global groq_model_cache

```
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
        timeout=15
    )

    if response.status_code != 200:
        return None

    data = response.json()

    models = data.get("data", [])

    available = []

    for model in models:
        model_id = model.get("id")

        if model_id:
            available.append(model_id)

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
            return preferred

    keywords = [
        "llama",
        "qwen",
        "gemma",
        "gpt"
    ]

    for keyword in keywords:
        for model_id in available:
            if keyword in model_id.lower():
                groq_model_cache = model_id
                return model_id

    if available:
        groq_model_cache = available[0]
        return available[0]

except Exception:
    return None

return None
```

# ============================================================

# GROQ

# ============================================================

def ask_groq(user_prompt):
if not GROQ_API_KEY:
return None

```
model = get_groq_model()

if not model:
    return None

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

messages = [
    {
        "role": "system",
        "content": SYSTEM_INSTRUCTION
    }
]

messages.extend(conversation_history)

messages.append({
    "role": "user",
    "content": user_prompt
})

payload = {
    "model": model,
    "messages": messages,
    "temperature": 0.7,
    "max_tokens": 700
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=45
    )

    if response.status_code != 200:
        print(
            "Groq error:",
            response.status_code,
            response.text
        )
        return None

    result = response.json()

    return result["choices"][0]["message"]["content"].strip()

except Exception as error:
    print("Groq exception:", error)
    return None
```

# ============================================================

# GEMINI FALLBACK

# ============================================================

def ask_gemini(user_prompt):
if not GEMINI_API_KEY:
return None

```
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

    if role == "assistant":
        gemini_role = "model"
    else:
        gemini_role = "user"

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
        "maxOutputTokens": 700
    }
}

try:
    response = requests.post(
        url,
        params=params,
        json=payload,
        timeout=45
    )

    if response.status_code != 200:
        print(
            "Gemini error:",
            response.status_code,
            response.text
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
    print("Gemini exception:", error)
    return None
```

# ============================================================

# AI RESPONSE ENGINE

# ============================================================

def generate_response(user_prompt):
user_prompt = user_prompt.strip()

```
if not user_prompt:
    return "I didn't catch that."

add_to_memory("user", user_prompt)

answer = ask_groq(user_prompt)

if not answer:
    answer = ask_gemini(user_prompt)

if not answer:
    answer = (
        "I'm unable to reach my language systems at the moment. "
        "Please try again shortly."
    )

add_to_memory("assistant", answer)

return answer
```

# ============================================================

# WEB UI

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
        Segoe UI,
        Arial,
        sans-serif;

    overflow: hidden;
}

#app {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
}

.top-label {
    position: absolute;
    top: 28px;
    left: 32px;

    font-size: 12px;
    letter-spacing: 4px;
    text-transform: uppercase;

    color: rgba(190, 210, 240, 0.55);
}

.system-status {
    position: absolute;
    top: 30px;
    right: 32px;

    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;

    color: rgba(150, 190, 230, 0.65);
}

.orb-container {
    width: 320px;
    height: 320px;

    position: relative;

    display: flex;
    align-items: center;
    justify-content: center;
}

.orb-ring {
    position: absolute;

    width: 250px;
    height: 250px;

    border-radius: 50%;

    border: 1px solid rgba(50, 145, 255, 0.16);

    animation: rotate 14s linear infinite;
}

.orb-ring:nth-child(2) {
    width: 290px;
    height: 290px;

    border-color: rgba(90, 130, 255, 0.10);

    animation-duration: 20s;
    animation-direction: reverse;
}

.orb-ring:nth-child(3) {
    width: 320px;
    height: 320px;

    border-color: rgba(120, 170, 255, 0.06);

    animation-duration: 28s;
}

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
        0 0 35px rgba(58, 130, 246, 0.75),
        0 0 90px rgba(58, 130, 246, 0.35),
        inset 0 0 40px rgba(255, 255, 255, 0.16);

    animation: breathe 3s ease-in-out infinite;

    position: relative;

    cursor: default;
}

.orb::before {
    content: "";

    position: absolute;

    inset: 14px;

    border-radius: 50%;

    border: 1px solid rgba(255,255,255,0.16);
}

.orb::after {
    content: "";

    position: absolute;

    width: 38px;
    height: 38px;

    left: 42px;
    top: 28px;

    border-radius: 50%;

    background: rgba(255,255,255,0.25);

    filter: blur(10px);
}

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
        0 0 40px rgba(39, 209, 127, 0.85),
        0 0 100px rgba(39, 209, 127, 0.40);
}

.state-processing .orb {
    background:
        radial-gradient(
            circle at 35% 30%,
            #e1c7ff 0%,
            #9b5cff 30%,
            #5420a8 60%,
            #19062f 100%
        );

    box-shadow:
        0 0 40px rgba(155, 92, 255, 0.85),
        0 0 100px rgba(155, 92, 255, 0.40);

    animation:
        breathe 1.2s ease-in-out infinite,
        spin-glow 2s linear infinite;
}

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
        0 0 45px rgba(220, 235, 255, 0.95),
        0 0 110px rgba(80, 150, 255, 0.50);

    animation: speaking 0.9s ease-in-out infinite;
}

.status {
    margin-top: 24px;

    font-size: 14px;
    letter-spacing: 3px;

    text-transform: uppercase;

    color: rgba(210, 225, 245, 0.70);

    min-height: 20px;

    text-align: center;
}

.response {
    width: min(720px, 82vw);

    margin-top: 24px;

    min-height: 48px;

    padding: 15px 20px;

    border: 1px solid rgba(100, 150, 220, 0.12);

    border-radius: 14px;

    background: rgba(7, 15, 28, 0.55);

    backdrop-filter: blur(14px);

    color: rgba(225, 235, 250, 0.86);

    font-size: 15px;
    line-height: 1.6;

    text-align: center;

    opacity: 0;

    transform: translateY(8px);

    transition:
        opacity 0.35s ease,
        transform 0.35s ease;
}

.response.visible {
    opacity: 1;
    transform: translateY(0);
}

.footer {
    position: absolute;

    bottom: 28px;

    font-size: 10px;

    letter-spacing: 5px;

    color: rgba(160, 180, 210, 0.35);

    text-transform: uppercase;
}

.mic-warning {
    display: none;

    position: absolute;

    bottom: 70px;

    padding: 10px 16px;

    border-radius: 10px;

    background: rgba(80, 20, 20, 0.55);

    border: 1px solid rgba(255, 100, 100, 0.2);

    color: rgba(255, 190, 190, 0.85);

    font-size: 12px;

    text-align: center;
}

@keyframes breathe {

    0%, 100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.035);
    }
}

@keyframes speaking {

    0%, 100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.07);
    }
}

@keyframes rotate {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

@keyframes spin-glow {

    from {
        filter: hue-rotate(0deg);
    }

    to {
        filter: hue-rotate(35deg);
    }
}

</style>

</head>

<body>

<div id="app">

```
<div class="top-label">
    STERLING
</div>

<div
    class="system-status"
    id="systemStatus"
>
    SYSTEM ONLINE
</div>

<div
    class="orb-container"
    id="orbContainer"
>

    <div class="orb-ring"></div>
    <div class="orb-ring"></div>
    <div class="orb-ring"></div>

    <div
        class="orb"
        id="orb"
    ></div>

</div>

<div
    class="status"
    id="status"
>
    STANDBY
</div>

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
```

</div>

<script>

let recognition = null;
let wakeRecognition = null;

let isProcessing = false;
let isSpeaking = false;

let wakeRestartTimer = null;

const orb = document.getElementById("orb");
const app = document.getElementById("app");
const statusElement = document.getElementById("status");
const responseElement = document.getElementById("response");
const systemStatus = document.getElementById("systemStatus");
const micWarning = document.getElementById("micWarning");


function setState(state, text) {

    app.classList.remove(
        "state-listening",
        "state-processing",
        "state-speaking"
    );

    if (state === "listening") {
        app.classList.add("state-listening");
    }

    if (state === "processing") {
        app.classList.add("state-processing");
    }

    if (state === "speaking") {
        app.classList.add("state-speaking");
    }

    statusElement.textContent = text;
}


function showResponse(text) {

    responseElement.textContent = text;

    responseElement.classList.add("visible");
}


function hideResponse() {

    responseElement.classList.remove("visible");
}


function getSpeechRecognition() {

    return (
        window.SpeechRecognition ||
        window.webkitSpeechRecognition ||
        null
    );
}


function cleanCommand(text) {

    if (!text) {
        return "";
    }

    let cleaned = text.trim();

    cleaned = cleaned.replace(
        /^\s*sterling[\s,:-]*/i,
        ""
    );

    return cleaned.trim();
}


function extractAfterWakeWord(text) {

    if (!text) {
        return "";
    }

    const match = text.match(
        /\bsterling\b(.*)/i
    );

    if (!match) {
        return "";
    }

    return match[1]
        .replace(/^[\s,:-]+/, "")
        .trim();
}


function createRecognition() {

    const Recognition = getSpeechRecognition();

    if (!Recognition) {
        return null;
    }

    const instance = new Recognition();

    instance.lang = "en-US";
    instance.continuous = false;
    instance.interimResults = false;
    instance.maxAlternatives = 1;

    return instance;
}


function stopWakeListener() {

    if (wakeRestartTimer) {
        clearTimeout(wakeRestartTimer);
        wakeRestartTimer = null;
    }

    if (wakeRecognition) {

        try {
            wakeRecognition.onend = null;
            wakeRecognition.stop();
        } catch (error) {
        }

        wakeRecognition = null;
    }
}


function startWakeListener() {

    if (isProcessing || isSpeaking) {
        return;
    }

    stopWakeListener();

    wakeRecognition = createRecognition();

    if (!wakeRecognition) {

        systemStatus.textContent =
            "VOICE UNSUPPORTED";

        statusElement.textContent =
            "USE CHROME OR EDGE";

        micWarning.style.display = "block";

        return;
    }

    wakeRecognition.onstart = function() {

        systemStatus.textContent =
            "LISTENING FOR WAKE WORD";

        setState(
            "standby",
            "STANDBY — SAY STERLING"
        );
    };


    wakeRecognition.onresult = function(event) {

        const result =
            event.results[
                event.results.length - 1
            ];

        if (!result || !result[0]) {
            return;
        }

        const transcript =
            result[0].transcript.trim();

        const lower =
            transcript.toLowerCase();

        if (!lower.includes("sterling")) {
            return;
        }

        stopWakeListener();

        const command =
            extractAfterWakeWord(transcript);

        if (command) {

            activateSterling(command);

        } else {

            activateSterling("");
        }
    };


    wakeRecognition.onerror = function(event) {

        if (
            event.error === "not-allowed" ||
            event.error === "service-not-allowed"
        ) {

            systemStatus.textContent =
                "MICROPHONE BLOCKED";

            statusElement.textContent =
                "ALLOW MICROPHONE ACCESS";

            micWarning.style.display = "block";

            return;
        }

        scheduleWakeRestart();
    };


    wakeRecognition.onend = function() {

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


function scheduleWakeRestart() {

    if (wakeRestartTimer) {
        return;
    }

    wakeRestartTimer = setTimeout(
        function() {

            wakeRestartTimer = null;

            if (
                !isProcessing &&
                !isSpeaking
            ) {
                startWakeListener();
            }

        },
        400
    );
}


function activateSterling(command) {

    stopWakeListener();

    if (command) {

        sendCommand(command);

        return;
    }

    setState(
        "speaking",
        "AWAITING COMMAND"
    );

    speak(
        "Yes?",
        function() {

            startCommandListener();

        }
    );
}


function startCommandListener() {

    stopWakeListener();

    recognition = createRecognition();

    if (!recognition) {

        statusElement.textContent =
            "VOICE UNSUPPORTED";

        return;
    }

    setState(
        "listening",
        "LISTENING"
    );

    recognition.onresult = function(event) {

        const result =
            event.results[
                event.results.length - 1
            ];

        if (!result || !result[0]) {
            return;
        }

        const transcript =
            result[0].transcript.trim();

        const command =
            cleanCommand(transcript);

        if (!command) {

            setState(
                "standby",
                "STANDBY — SAY STERLING"
            );

            startWakeListener();

            return;
        }

        recognition.stop();

        sendCommand(command);
    };


    recognition.onerror = function(event) {

        if (
            event.error === "not-allowed" ||
            event.error === "service-not-allowed"
        ) {

            micWarning.style.display = "block";

            statusElement.textContent =
                "ALLOW MICROPHONE ACCESS";

            return;
        }

        setState(
            "standby",
            "STANDBY — SAY STERLING"
        );

        startWakeListener();
    };


    recognition.onend = function() {

        if (
            !isProcessing &&
            !isSpeaking &&
            statusElement.textContent === "LISTENING"
        ) {

            setState(
                "standby",
                "STANDBY — SAY STERLING"
            );

            startWakeListener();
        }
    };


    try {

        recognition.start();

    } catch (error) {

        setState(
            "standby",
            "STANDBY — SAY STERLING"
        );

        startWakeListener();
    }
}


async function sendCommand(command) {

    if (!command || isProcessing) {
        return;
    }

    isProcessing = true;

    stopWakeListener();

    if (recognition) {

        try {
            recognition.stop();
        } catch (error) {
        }

        recognition = null;
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
            encodeURIComponent(command);

        const response =
            await fetch(url, {
                method: "GET"
            });


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


        showResponse(answer);

        isProcessing = false;

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

        showResponse(message);

        isProcessing = false;

        speak(
            message,
            function() {

                returnToStandby();

            }
        );
    }
}


function speak(text, onComplete) {

    if (!("speechSynthesis" in window)) {

        if (onComplete) {
            onComplete();
        }

        return;
    }

    isSpeaking = true;

    stopWakeListener();

    window.speechSynthesis.cancel();

    const utterance =
        new SpeechSynthesisUtterance(text);

    utterance.lang = "en-US";

    utterance.rate = 0.96;

    utterance.pitch = 0.95;

    utterance.volume = 1.0;


    const voices =
        window.speechSynthesis.getVoices();


    const preferredNames = [
        "Microsoft Guy Online",
        "Microsoft Ryan Online",
        "Microsoft Christopher Online",
        "Google US English",
        "Google UK English Male",
        "Samantha",
        "Daniel"
    ];


    let selectedVoice = null;


    for (const preferred of preferredNames) {

        selectedVoice =
            voices.find(
                voice =>
                    voice.name
                        .toLowerCase()
                        .includes(
                            preferred.toLowerCase()
                        )
            );

        if (selectedVoice) {
            break;
        }
    }


    if (!selectedVoice) {

        selectedVoice =
            voices.find(
                voice =>
                    voice.lang === "en-US"
            );
    }


    if (!selectedVoice) {

        selectedVoice =
            voices.find(
                voice =>
                    voice.lang.startsWith("en")
            );
    }


    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }


    utterance.onstart = function() {

        setState(
            "speaking",
            "SPEAKING"
        );

        systemStatus.textContent =
            "STERLING SPEAKING";
    };


    utterance.onend = function() {

        isSpeaking = false;

        if (onComplete) {
            onComplete();
        }
    };


    utterance.onerror = function() {

        isSpeaking = false;

        if (onComplete) {
            onComplete();
        }
    };


    window.speechSynthesis.speak(
        utterance
    );
}


function returnToStandby() {

    isProcessing = false;
    isSpeaking = false;

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
        500
    );
}


function initialiseSterling() {

    if (
        !window.isSecureContext &&
        location.hostname !== "localhost"
    ) {

        console.warn(
            "Microphone access may require HTTPS."
        );
    }


    if (!getSpeechRecognition()) {

        systemStatus.textContent =
            "VOICE UNSUPPORTED";

        statusElement.textContent =
            "USE CHROME OR EDGE";

        micWarning.style.display = "block";

        return;
    }


    if ("speechSynthesis" in window) {

        window.speechSynthesis.getVoices();

        window.speechSynthesis.onvoiceschanged =
            function() {

                window.speechSynthesis.getVoices();

            };
    }


    setTimeout(
        function() {

            startWakeListener();

        },
        700
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
response_class=HTMLResponse
)
async def home():
return HTMLResponse(
content=ORB_UI_HTML
)

@app.get("/api/chat")
async def chat(
prompt: str = Query(
...,
min_length=1
)
):

```
response = generate_response(prompt)

return {
    "sterling_response": response
}
```

@app.get("/api/status")
async def status():

```
return {
    "status": "online",
    "system": "STERLING",
    "groq_configured": bool(GROQ_API_KEY),
    "gemini_configured": bool(GEMINI_API_KEY),
    "conversation_memory": len(
        conversation_history
    )
}
```

@app.get("/health")
async def health():

```
return {
    "status": "healthy"
}
```

# ============================================================

# OPTIONAL WEBSOCKET PLACEHOLDER

# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket):

```
await websocket.accept()

try:

    while True:

        data = await websocket.receive_text()

        response = generate_response(data)

        await websocket.send_json({
            "sterling_response": response
        })

except Exception as error:

    print(
        "WebSocket closed:",
        error
    )

