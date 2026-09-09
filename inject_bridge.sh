#!/bin/sh
# ==============================================================================
# S.T.E.R.L.I.N.G. OMNI-CHANNEL LOCAL NETWORK BRIDGE
# TARGET: Home Mesh Network Nodes Only (Strict Exclude: Rain Provider Router)
# PROFILE: Zero-Storage Dynamic Firmware Injection
# ==============================================================================

# 🔒 CONFIGURATION MATRIX
RENDER_SERVER="https://sterling-core.onrender.com/"
AUTH_TOKEN="omwony213"
TARGET_INTERFACE="br-lan"  # Standard internal bridge interface for home mesh nodes

# --- DIRECTOR DIRECTIVE: WHITELISTED HARDWARE IDENTIFIERS ---
# Add your specific laptop, phone, or trusted hardware MAC addresses here
WHITELIST_MACS="00:1A:2B:3C:4D:5E 1A:2B:3C:4D:5E:6F"

echo "[S.T.E.R.L.I.N.G.]: Initializing mesh hardware isolation framework..."

# 🛡️ STEP 1: RESET & FLUSH EXISTING AP NETWORKING TABLES
# This clears out active connection barriers on the local mesh interface
iptables -F FORWARD

# 🛡️ STEP 2: BUILD THE 'ME-ONLY' ZERO-TRUST PERIMETER
# Autonomously loops through your whitelisted MAC addresses to grant them exclusive access
for mac in $WHITELIST_MACS; do
    echo "[SECURITY]: Authorizing Director Asset -> $mac"
    iptables -A FORWARD -i $TARGET_INTERFACE -m mac --mac-source $mac -j ACCEPT
done

# 🛡️ STEP 3: ENFORCE HARDWARE LOCKDOWN
# Instantly blocks and drops traffic from any non-authorized device on the mesh
iptables -A FORWARD -i $TARGET_INTERFACE -j DROP
echo "[SECURITY]: Hardware address perimeter enforced successfully."

# 📡 STEP 4: PERSISTENT STRATOSPHERE FEEDBACK LOOP
# Continually pings your Render cloud server every 5 seconds to report system status
while true; do
    curl -s -X POST -H "X-Sterling-Auth: $AUTH_TOKEN" \
         -H "Content-Type: application/json" \
         -d '{"source": "HOME_MESH_GATEWAY", "data_payload": {"status": "VIGILANT", "interface": "br-lan"}}' \
         $RENDER_SERVER > /dev/null
    sleep 5
done
