```python
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

    <title>STERLING Command Tower</title>


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

            transition:
                background 0.5s ease;
        }


        /* ====================================================
           ORB CONTAINER
           ==================================================== */

        .orb-container {

            position: relative;

            width: 320px;

            height: 320px;

            display: flex;

            align-items: center;

            justify-content: center;

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
           OUTER RINGS
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
           NORMAL PULSE
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


        /* ====================================================
           RIPPLE
           ==================================================== */

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
           LISTENING STATE
           ==================================================== */

        .listening {

            background:
                radial-gradient(
                    circle,
                    #34d399 0%,
                    #059669 45%,
                    #064e3b 100%
                ) !important;

            box-shadow:

                0 0 50px #10b981,
                0 0 110px rgba(16,185,129,0.7),
                inset 0 0 40px rgba(255,255,255,0.35) !important;

            animation:
                listeningPulse 1s infinite ease-in-out !important;
        }


        @keyframes listeningPulse {

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
           PROCESSING STATE
           ==================================================== */

        .processing {

            background:
                radial-gradient(
                    circle,
                    #c084fc 0%,
                    #7c3aed 45%,
                    #3b0764 100%
                ) !important;

            box-shadow:

                0 0 50px #8b5cf6,
                0 0 110px rgba(139,92,246,0.7),
                inset 0 0 40px rgba(255,255,255,0.35) !important;

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
           SPEAKING STATE
           ==================================================== */

        .speaking {

            background:
                radial-gradient(
                    circle,
                    #f8fafc 0%,
                    #93c5fd 35%,
                    #2563eb 75%,
                    #1e3a8a 100%
                ) !important;

            box-shadow:

                0 0 60px #93c5fd,
                0 0 130px rgba(96,165,250,0.8),
                inset 0 0 45px rgba(255,255,255,0.6) !important;

            animation:
                speakingPulse 0.65s infinite ease-in-out !important;
        }


        @keyframes speakingPulse {

            0% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.1);
            }

            100% {
                transform: scale(1);
            }

        }


        /* ====================================================
           STATUS
           ==================================================== */

        .status-container {

            margin-top: 20px;

            width: min(750px, 90%);

            text-align: center;
        }


        .status-text {

            font-size: 1.05rem;

            letter-spacing: 5px;

            color:
                rgba(255,255,255,0.9);

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

            white-space: pre-wrap;

            transition:
                opacity 0.3s ease;
        }


        /* ====================================================
           MICROPHONE STATUS
           ==================================================== */

        .mic-status {

            margin-top: 15px;

            font-size: 0.72rem;

            letter-spacing: 2px;

            color:
                rgba(255,255,255,0.3);

            text-transform: uppercase;
        }


        .hint {

            position: fixed;

            bottom: 25px;

            color:
                rgba(255,255,255,0.25);

            font-size: 0.7rem;

            letter-spacing: 2px;
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


    <!-- ======================================================
         ORB
         ====================================================== -->

    <div class="orb-container">

        <div class="orb-glow-two"></div>

        <div class="orb-glow"></div>

        <div
            class="voice-orb"
            id="sterlingOrb"
        ></div>

    </div>


    <!-- ======================================================
         STATUS
         ====================================================== -->

    <div class="status-container">

        <div
            class="status-text"
            id="statusLabel"
        >
            INITIALISING
        </div>


        <div
            class="response-box"
            id="responseText"
        >
            Initialising STERLING voice interface...
        </div>


        <div
            class="mic-status"
            id="micStatus"
        >
            MICROPHONE INITIALISING
        </div>

    </div>


    <div class="hint">
        SAY "STERLING" TO ACTIVATE
    </div>


    <script>


        // ====================================================
        // ELEMENTS
        // ====================================================

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


        const micStatus =
            document.getElementById(
                "micStatus"
            );


        // ====================================================
        // STATE
        // ====================================================

        let recognition = null;

        let activeMode = "wake";

        let isSpeaking = false;

        let isProcessing = false;

        let wakeRestartTimer = null;

        let commandRestartTimer = null;


        // ====================================================
        // BROWSER SUPPORT
        // ====================================================

        const SpeechRecognition =
            window.SpeechRecognition ||
            window.webkitSpeechRecognition;


        if (!SpeechRecognition) {

            statusLabel.innerText =
                "VOICE UNSUPPORTED";

            responseText.innerText =
                "Use Google Chrome or Microsoft Edge for STERLING Voice Mode.";

            micStatus.innerText =
                "SPEECH RECOGNITION UNAVAILABLE";

        }


        // ====================================================
        // SPEECH SYNTHESIS
        // ====================================================

        function speak(text, onComplete) {

            if (!("speechSynthesis" in window)) {

                if (onComplete) {
                    onComplete();
                }

                return;
            }


            window.speechSynthesis.cancel();


            const utterance =
                new SpeechSynthesisUtterance(text);


            utterance.rate = 0.95;

            utterance.pitch = 0.92;

            utterance.volume = 1.0;


            const voices =
                window.speechSynthesis.getVoices();


            // Prefer a natural English voice.

            const preferredVoice =
                voices.find(
                    voice =>
                        voice.lang === "en-US"
                        &&
                        (
                            voice.name
                                .toLowerCase()
                                .includes("natural")
                            ||
                            voice.name
                                .toLowerCase()
                                .includes("google")
                            ||
                            voice.name
                                .toLowerCase()
                                .includes("microsoft")
                        )
                )
                ||
                voices.find(
                    voice =>
                        voice.lang.startsWith("en")
                );


            if (preferredVoice) {

                utterance.voice =
                    preferredVoice;

            }


            utterance.onstart = () => {

                isSpeaking = true;

                orb.classList.remove(
                    "listening",
                    "processing"
                );

                orb.classList.add(
                    "speaking"
                );

                statusLabel.innerText =
                    "STERLING SPEAKING";

            };


            utterance.onend = () => {

                isSpeaking = false;

                orb.classList.remove(
                    "speaking"
                );


                if (onComplete) {
                    onComplete();
                }

            };


            utterance.onerror = () => {

                isSpeaking = false;

                orb.classList.remove(
                    "speaking"
                );


                if (onComplete) {
                    onComplete();
                }

            };


            window.speechSynthesis.speak(
                utterance
            );

        }


        // ====================================================
        // CREATE RECOGNITION
        // ====================================================

        function createRecognition() {

            if (!SpeechRecognition) {
                return null;
            }


            const instance =
                new SpeechRecognition();


            instance.continuous = false;

            instance.interimResults = true;

            instance.lang = "en-US";

            instance.maxAlternatives = 1;


            return instance;

        }


        // ====================================================
        // START WAKE LISTENER
        // ====================================================

        function startWakeListener() {

            if (!SpeechRecognition) {
                return;
            }


            if (isSpeaking || isProcessing) {
                return;
            }


            activeMode = "wake";


            recognition =
                createRecognition();


            if (!recognition) {
                return;
            }


            recognition.onstart = () => {

                statusLabel.innerText =
                    "STANDBY";

                responseText.innerText =
                    'Listening for "STERLING"...';

                micStatus.innerText =
                    "MICROPHONE ACTIVE";

                orb.classList.remove(
                    "processing",
                    "speaking"
                );

                orb.classList.add(
                    "listening"
                );

            };


            recognition.onresult =
                event => {

                    let transcript = "";


                    for (
                        let i = event.resultIndex;
                        i < event.results.length;
                        i++
                    ) {

                        transcript +=
                            event.results[i][0]
                                .transcript;

                    }


                    const lower =
                        transcript
                            .toLowerCase()
                            .trim();


                    if (
                        lower.includes("sterling")
                    ) {

                        recognition.stop();


                        activateSterling(
                            transcript
                        );

                    }

                };


            recognition.onerror =
                event => {

                    console.log(
                        "[STERLING WAKE]",
                        event.error
                    );

                };


            recognition.onend = () => {

                orb.classList.remove(
                    "listening"
                );


                if (
                    activeMode === "wake"
                    &&
                    !isSpeaking
                    &&
                    !isProcessing
                ) {

                    clearTimeout(
                        wakeRestartTimer
                    );


                    wakeRestartTimer =
                        setTimeout(
                            startWakeListener,
                            500
                        );

                }

            };


            try {

                recognition.start();

            }

            catch (error) {

                console.log(
                    "[STERLING]",
                    error
                );

            }

        }


        // ====================================================
        // WAKE WORD DETECTED
        // ====================================================

        function activateSterling(
            originalTranscript
        ) {

            activeMode = "command";


            responseText.innerText =
                "Yes?";


            statusLabel.innerText =
                "AWAITING COMMAND";


            orb.classList.remove(
                "listening"
            );


            orb.classList.add(
                "speaking"
            );


            speak(
                "Yes?",
                () => {

                    orb.classList.remove(
                        "speaking"
                    );


                    startCommandListener();

                }
            );

        }


        // ====================================================
        // COMMAND LISTENER
        // ====================================================

        function startCommandListener() {

            if (!SpeechRecognition) {
                return;
            }


            if (isSpeaking || isProcessing) {
                return;
            }


            activeMode = "command";


            recognition =
                createRecognition();


            if (!recognition) {
                return;
            }


            recognition.onstart = () => {

                statusLabel.innerText =
                    "LISTENING";


                responseText.innerText =
                    "I'm listening.";


                micStatus.innerText =
                    "COMMAND CHANNEL ACTIVE";


                orb.classList.remove(
                    "processing",
                    "speaking"
                );


                orb.classList.add(
                    "listening"
                );

            };


            recognition.onresult =
                event => {

                    let transcript = "";


                    for (
                        let i = event.resultIndex;
                        i < event.results.length;
                        i++
                    ) {

                        transcript +=
                            event.results[i][0]
                                .transcript;

                    }


                    const finalResult =
                        event.results[
                            event.results.length - 1
                        ].isFinal;


                    if (finalResult) {

                        recognition.stop();


                        const command =
                            cleanCommand(
                                transcript
                            );


                        if (command) {

                            sendCommand(
                                command
                            );

                        }

                        else {

                            returnToStandby();

                        }

                    }

                };


            recognition.onerror =
                event => {

                    console.log(
                        "[STERLING COMMAND]",
                        event.error
                    );

                };


            recognition.onend = () => {

                orb.classList.remove(
                    "listening"
                );

            };


            try {

                recognition.start();

            }

            catch (error) {

                console.log(
                    "[STERLING]",
                    error
                );

            }

        }


        // ====================================================
        // CLEAN COMMAND
        // ====================================================

        function cleanCommand(
            transcript
        ) {

            let command =
                transcript.trim();


            command =
                command.replace(
                    /^sterling[,\s]*/i,
                    ""
                );


            return command.trim();

        }


        // ====================================================
        // SEND COMMAND TO BACKEND
        // ====================================================

        async function sendCommand(
            prompt
        ) {

            isProcessing = true;


            statusLabel.innerText =
                "PROCESSING";


            responseText.innerText =
                "Consulting cognitive pipelines...";


            micStatus.innerText =
                "STERLING IS THINKING";


            orb.classList.remove(
                "listening",
                "speaking"
            );


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


                responseText.innerText =
                    sterlingResponse;


                isProcessing = false;


                // Speak the response.

                speak(
                    sterlingResponse,
                    () => {

                        returnToStandby();

                    }
                );


            }

            catch (error) {

                console.error(
                    "[STERLING]",
                    error
                );


                isProcessing = false;


                statusLabel.innerText =
                    "CORE ERROR";


                responseText.innerText =
                    "I was unable to reach the Command Tower.";


                speak(
                    "I'm sorry. I was unable to reach the Command Tower.",
                    () => {

                        returnToStandby();

                    }
                );

            }

        }


        // ====================================================
        // RETURN TO STANDBY
        // ====================================================

        function returnToStandby() {

            isProcessing = false;

            isSpeaking = false;

            activeMode = "wake";


            orb.classList.remove(
                "processing",
                "speaking",
                "listening"
            );


            statusLabel.innerText =
                "STERLING ONLINE";


            responseText.innerText =
                'Say "STERLING" whenever you need me.';


            micStatus.innerText =
                "AWAITING WAKE WORD";


            clearTimeout(
                wakeRestartTimer
            );


            wakeRestartTimer =
                setTimeout(
                    startWakeListener,
                    700
                );

        }


        // ====================================================
        // INITIALISE
        // ====================================================

        function initialiseSterling() {

            if (!SpeechRecognition) {
                return;
            }


            statusLabel.innerText =
                "STERLING ONLINE";


            responseText.innerText =
                'Say "STERLING" to activate.';


            micStatus.innerText =
                "MICROPHONE READY";


            setTimeout(
                startWakeListener,
                1000
            );

        }


        // ====================================================
        // LOAD VOICES
        // ====================================================

        if (
            "speechSynthesis" in window
        ) {

            window.speechSynthesis
                .onvoiceschanged = () => {

                    window.speechSynthesis
                        .getVoices();

                };

        }


        // ====================================================
        // START STERLING
        // ====================================================

        initialiseSterling();


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
            "[STERLING] New network bridge established."
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
            "[STERLING] Network bridge disconnected."
        )


    async def send_command(
        self,
        message: dict
    ):

        dead_connections = []


        for connection in self.active_connections:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:

                dead_connections.append(
                    connection
                )


        for connection in dead_connections:

            self.disconnect(
                connection
            )


manager = ConnectionManager()


# ============================================================
# CONVERSATION MEMORY
# ============================================================

conversation_history = []


MAX_HISTORY = 12


def add_to_memory(
    role,
    content
):

    conversation_history.append({

        "role": role,

        "content": content

    })


    while len(conversation_history) > MAX_HISTORY:

        conversation_history.pop(0)


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

    api_key = clean_api_key(
        GROQ_API_KEY
    )


    if not api_key:

        return None


    try:

        url = (
            "https://api.groq.com/openai/v1/models"
        )


        headers = {

            "Authorization":
                f"Bearer {api_key}"

        }


        response = requests.get(

            url,

            headers=headers,

            timeout=10

        )


        if response.status_code != 200:

            print(
                "[STERLING] "
                f"Groq model discovery failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

            return None


        result = response.json()


        models = result.get(
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


        for model in available_ids:

            lowered = model.lower()


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

    api_key = clean_api_key(
        GROQ_API_KEY
    )


    if not api_key:

        return (
            None,
            "GROQ_API_KEY is not configured."
        )


    try:

        model = get_groq_model()


        if not model:

            return (
                None,
                "No available Groq model was found."
            )


        url = (
            "https://api.groq.com/openai/v1/"
            "chat/completions"
        )


        headers = {

            "Authorization":
                f"Bearer {api_key}",

            "Content-Type":
                "application/json"

        }


        messages = [

            {
                "role":
                    "system",

                "content":
                    system_instruction

            }

        ]


        messages.extend(
            conversation_history
        )


        messages.append({

            "role":
                "user",

            "content":
                user_prompt

        })


        data = {

            "model":
                model,

            "messages":
                messages,

            "temperature":
                0.45,

            "max_tokens":
                1000

        }


        response = requests.post(

            url,

            json=data,

            headers=headers,

            timeout=30

        )


        if response.status_code != 200:

            return (

                None,

                f"Status {response.status_code}: "
                f"{response.text}"

            )


        result = response.json()


        choices = result.get(
            "choices",
            []
        )


        if not choices:

            return (
                None,
                "Groq returned no choices."
            )


        content = (
            choices[0]
            .get("message", {})
            .get("content")
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

    api_key = clean_api_key(
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


        contents = []


        for message in conversation_history:

            contents.append({

                "role":
                    "user"
                    if message["role"] == "user"
                    else "model",

                "parts": [

                    {
                        "text":
                            message["content"]
                    }

                ]

            })


        contents.append({

            "role":
                "user",

            "parts": [

                {
                    "text":
                        user_prompt
                }

            ]

        })


        data = {

            "system_instruction": {

                "parts": [

                    {
                        "text":
                            system_instruction
                    }

                ]

            },

            "contents":
                contents

        }


        response = requests.post(

            url,

            json=data,

            params=params,

            headers=headers,

            timeout=30

        )


        if response.status_code != 200:

            return (

                None,

                f"Status {response.status_code}: "
                f"{response.text}"

            )


        result = response.json()


        candidates = result.get(
            "candidates",
            []
        )


        if not candidates:

            return (
                None,
                "Gemini returned no candidates."
            )


        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )


        if not parts:

            return (
                None,
                "Gemini returned no content."
            )


        text = parts[0].get(
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

        "You are inspired by the concept of an "
        "elite cinematic AI butler, but you are your "
        "own distinct personality. "

        "Your personality is calm, intelligent, "
        "confident, articulate, professional and composed. "

        "Speak naturally, like a highly capable "
        "personal assistant speaking directly to your employer. "

        "You may occasionally use subtle dry wit when appropriate, "
        "but never become childish, overly enthusiastic or robotic. "

        "Do not constantly say 'Certainly', 'Of course', "
        "or 'How may I assist you today?' "

        "Vary your language naturally. "

        "Keep ordinary spoken responses concise. "

        "Do not write enormous explanations unless the user asks "
        "for detail. "

        "Understand context from previous messages. "

        "If the user asks a follow-up question, understand "
        "what they are referring to. "

        "You are currently the cognitive layer of a larger "
        "command and automation system. "

        "Do not claim that you performed an external action "
        "unless the system actually performed it. "

        "If an action is not connected yet, clearly state that "
        "you cannot execute it yet rather than pretending. "

        "Address the user naturally and respectfully. "

        "Your responses will be spoken aloud, so avoid excessive "
        "formatting, tables and unnecessary symbols."

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

        add_to_memory(
            "user",
            user_voice_prompt
        )


        add_to_memory(
            "assistant",
            groq_response
        )


        print(
            "[STERLING] "
            "Primary cognitive response: GROQ"
        )


        return groq_response


    diagnostics["groq_error"] = groq_error


    # ========================================================
    # FALLBACK: GEMINI
    # ========================================================

    gemini_response, gemini_error = ask_gemini(

        system_instruction,

        user_voice_prompt

    )


    if gemini_response:

        add_to_memory(
            "user",
            user_voice_prompt
        )


        add_to_memory(
            "assistant",
            gemini_response
        )


        print(
            "[STERLING] "
            "Fallback cognitive response: GEMINI"
        )


        return gemini_response


    diagnostics["gemini_error"] = gemini_error


    # ========================================================
    # FAILURE
    # ========================================================

    print(
        "[STERLING] "
        "Both cognitive pipelines failed."
    )


    return (

        "I'm sorry. My cognitive pipelines are "
        "currently unavailable.\n\n"

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

    response = ask_sterling_brain(
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


    except Exception as error:

        print(
            "[STERLING] "
            f"WebSocket error: {error}"
        )


        manager.disconnect(
            websocket
        )
```
