import os
import sys
import logging
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from core.detect import OSDetector
from core.agent import HybridAgent
from core.executor import ExecutorFactory
import psutil
import json

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("jarvis.main")

app = FastAPI(title="Project JARVIS Core")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os_detector = OSDetector()
runtime_os = os_detector.detect_environment()

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing JARVIS Core...")
    logger.info(f"Running on: {runtime_os}")
    
    # 1. Root Check
    if runtime_os == "linux":
        if os.geteuid() != 0:
            logger.warning("⚠️  PERMISSION WARNING: Agent is NOT running as root!")
            logger.warning("    System commands (apt, iptables) may fail or ask for passwords.")
            logger.warning("    RECOMMENDATION: Stop and restart with 'sudo python main.py'")
        else:
            logger.info("✅ Running with ROOT privileges. Full system control active.")

        try:
            os.nice(10) 
            logger.info("Process priority lowered (nice=10) for Eco-Mode.")
        except Exception as e:
            logger.warning(f"Could not adjust nice value: {e}")

@app.get("/")
def read_root():
    return {"status": "active", "os": runtime_os, "mode": "eco-silent"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to WebSocket")
    
    
    # Instantiate Agent and Real Executor
    agent = HybridAgent()
    try:
        executor = ExecutorFactory.get_executor(runtime_os)
        logger.info(f"Loaded Executor for: {runtime_os}")
    except ValueError as e:
        logger.error(str(e))
        executor = None # Should handle gracefully
    
    # Session State
    pending_action = None
    
    try:
        while True:
            # 1. Receive & Process User Command
            # We need a way to listen for messages AND push stats. 
            # Solution: asyncio.gather or simple timeout loop? 
            # Better: Use a separate task for receiving or just rely on the frontend to push, 
            # but we need to push stats periodically. 
            
            # Pattern: Infinite loop with timeout to allow sending stats if no msg received? 
            # Or separate Producer/Consumer tasks.
            # Simplified for PoC: Receive with timeout.
            
            # Init stats refs
            net_init = psutil.net_io_counters()
            prev_net_sent = net_init.bytes_sent
            prev_net_recv = net_init.bytes_recv
            
            try:
                # Wait for command with 1.0s timeout (Acts as 1Hz heartbeat)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                cmd = json.loads(data)
                logger.info(f"Received CMD: {cmd}")
                
                # Command Routing
                msg_type = cmd.get("type")
                
                if msg_type == "control":
                    mode = cmd.get("mode")
                    reply = f"System Mode Switched to: {mode.upper()}"
                    # TODO: Call agent.set_mode(mode)
                
                elif msg_type == "chat":
                    user_msg = cmd.get("msg")
                    
                    # 1. Check if user is confirming a pending action
                    if pending_action and user_msg.lower() in ["yes", "confirm", "approve", "ok"]:
                        # Execute the pending action
                        logger.info(f"User approved action: {pending_action['action']}")
                        # Pass bypass_validator=True to prevent infinite approval loop
                        result = await agent.execute_action(pending_action, executor, bypass_validator=True)
                        
                        action_name = pending_action['action']
                        if action_name == "simulate_attack":
                             await websocket.send_json({
                                "type": "threat_alert",
                                "level": "critical",
                                "msg": "SYN Flood Attack Detected from 192.168.0.44"
                            })
                             reply = "⚠️ SECURITY DRILL INITIATED."
                        else:
                            # Show the actual output from the executor
                            output_log = result.get('msg', 'No Output')
                            reply = f"Action '{action_name}' Result:\n{output_log}"
                            
                        pending_action = None
                        
                    elif pending_action and user_msg.lower() in ["no", "cancel", "deny"]:
                        reply = "Action cancelled by user."
                        pending_action = None
                        
                    else:
                        # 2. Normal Agent Processing
                        # Parse Intent
                        intent = agent.process_input("", user_msg)
                        
                        # Try to Execute
                        # We need to modify execute_action to return the status so we can handle it here
                        result = await agent.execute_action(intent, executor)
                        
                        if result["status"] == "approval_required":
                             pending_action = intent # Store specifically the intent wrapper
                             reply = f"⚠️ APPROVAL REQUIRED: {result['msg']} \nType 'yes' to proceed."
                        elif result["status"] == "blocked":
                             reply = f"⛔ {result['msg']}"
                        elif result["status"] == "done":
                             reply = result["msg"]
                             # Special handling for resolve
                             if intent.get("action") == "resolve_threat":
                                 await websocket.send_json({"type": "threat_alert", "level": "safe", "msg": "Threat Neutralized."})
                        else:
                             reply = intent.get("reply", "I heard you.")
                
                else:
                    reply = "Unknown Command Protocol"

                # Send Confirmation
                await websocket.send_json({
                    "type": "log", 
                    "user": "System", 
                    "msg": reply, 
                    "isAi": True
                })
                
            except asyncio.TimeoutError:
                pass # No command, proceed to regular updates
            
            # 2. Push System Stats
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            
            # Network Speed Calculation (Delta)
            net = psutil.net_io_counters()
            bytes_sent = net.bytes_sent
            bytes_recv = net.bytes_recv
            
            # Calculate speed (Bytes/sec) - assuming ~1s interval
            # In a production app, use precise time deltas
            speed_sent = bytes_sent - prev_net_sent
            speed_recv = bytes_recv - prev_net_recv
            
            prev_net_sent = bytes_sent
            prev_net_recv = bytes_recv
            
            payload = {
                "type": "stats",
                "data": {
                    "cpu": cpu,
                    "ram": ram,
                    "net_sent_speed": speed_sent,
                    "net_recv_speed": speed_recv
                }
            }
            
            await websocket.send_json(payload)
            # await asyncio.sleep(1) # Interval handled by wait_for timeout implicitly? 
            # No, wait_for returns immediately if no msg. We need explicit sleep to prevent busy loop if no msg.
            # Actually, if we use timeout=1.0, it acts as the interval.
            
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
    finally:
        logger.info("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
