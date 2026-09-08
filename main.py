from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="S.T.E.R.L.I.N.G. Cloud Command Tower")

# SECURITY CONFIGURATION: Define your master credentials here
MASTER_PASSWORD = "omwony213"  # Change this to your secure passphrase
connected_devices: Dict[str, Dict[str, Any]] = {}
pending_commands: Dict[str, list] = {}

class CommandPayload(BaseModel):
    target_device: str
    action: str
    parameters: Optional[Dict[str, Any]] = None

class HeartbeatPayload(BaseModel):
    device_id: str
    device_type: str

def verify_access_token(x_sterling_auth: Optional[str] = Header(None)):
    """Verifies that incoming requests match your master password."""
    if not x_sterling_auth or x_sterling_auth != MASTER_PASSWORD:
        raise HTTPException(status_code=401, detail="Access Denied. Unauthorized signature.")
    return x_sterling_auth

@app.get("/")
def keep_alive_ping():
    """Endpoint for cron-job.org to ping every 10 mins to prevent cold starts."""
    return {"status": "ONLINE", "message": "S.T.E.R.L.I.N.G. Core Brain is fully active."}

@app.post("/api/v1/heartbeat")
def device_heartbeat(payload: HeartbeatPayload, auth: str = Depends(verify_access_token)):
    """Allows your online laptop/phone to announce they are ready for commands."""
    connected_devices[payload.device_id] = {
        "type": payload.device_type,
        "status": "ONLINE"
    }
    # Retrieve any commands waiting for this specific device
    device_queue = pending_commands.pop(payload.device_id, [])
    return {"status": "ACKNOWLEDGED", "queued_commands": device_queue}

@app.post("/api/v1/execute")
def process_voice_intent(payload: CommandPayload, auth: str = Depends(verify_access_token)):
    """Receives voice intents and routes them to the correct device queue."""
    if payload.target_device not in connected_devices:
        return {"status": "QUEUED", "message": f"{payload.target_device} is offline. Action queued."}
    
    if payload.target_device not in pending_commands:
        pending_commands[payload.target_device] = []
        
    pending_commands[payload.target_device].append({
        "action": payload.action,
        "parameters": payload.parameters
    })
    return {"status": "ROUTED", "message": f"Command forwarded to {payload.target_device} successfully."}
