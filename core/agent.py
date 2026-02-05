import json
import logging
from typing import Dict, Any, List
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from core.validator import SecurityValidator, ActionStatus
from core.executor import CommandExecutor

logger = logging.getLogger("jarvis.core.agent")

class HybridAgent:
    """
    Implements the 'Hybrid Intelligence' strategy.
    Internal thoughts/actions are strictly JSON for precision.
    External communication is Natural Language for UX.
    """
    
    def __init__(self, use_llm=False):
        self.use_llm = use_llm
        self.validator = SecurityValidator()
        # Mock system prompt
        self.system_prompt = """
        You are JARVIS, an AI System Administrator.
        Rules:
        1. Think in JSON.
        2. Your primary output format must be a valid JSON object.
        3. The JSON object should have keys: 'thought' (internal reasoning), 'action' (command to run), 'param' (arguments), and 'reply' (natural language for user).
        4. If no action is needed, set 'action' to null.
        
        Example:
        {
          "thought": "User asked for CPU usage. I should run the monitor tool.",
          "action": "check_cpu",
          "param": {},
          "reply": "Checking CPU status for you, sir."
        }
        """
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=self.system_prompt)
            logger.info("🧠 Brain Activated: Connected to Google Gemini API.")
        else:
            logger.warning("⚠️ Brain Missing: GEMINI_API_KEY not found. Running in Reflex Mode (Regex).")

    def process_input(self, context_summary: str, user_query: str) -> Dict[str, Any]:
        """
        Main loop:
        1. Receive condensed context & query.
        2. (Mock) Call LLM to get JSON response.
        3. Parse JSON.
        4. Return structured intent.
        """
        
        # --- Mocking LLM Response for Phase 1 ---
        # Real implementation would call OpenAI/Anthropic/LocalLLM API here
        # payload = mk_prompt(self.system_prompt, context_summary, user_query)
        # response_text = call_llm(payload)
        
        logger.info(f"Processing Query: {user_query}")
        
        # 1. Real Intelligence (The Brain - Gemini)
        if self.api_key and genai:
            try:
                # Gemini call with JSON mode enforcement
                response = self.model.generate_content(
                    f"Context: {context_summary}\n\nUser: {user_query}",
                    generation_config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"Brain Freeze (Gemini Error): {e}")
                # Fallback to reflex
        
        # 2. Reflex Mode (The Spinal Cord) - Fallback
        mock_response = {}
        
        q = user_query.lower()
        if "cpu" in q or "status" in q:
            mock_response = {
                "thought": "User wants system status. Using system_monitor skill.",
                "action": "system_monitor",
                "param": {},
                "reply": "System status coming right up."
            }
        elif "simulate" in q and "attack" in q:
            mock_response = {
                "thought": "User wants to test security alerts. This is a restricted action.",
                "action": "simulate_attack",
                "param": {},
                "reply": "Initiating Security Drill Protocol..."
            }
        elif ("update" in q or "upgrade" in q) and ("apt" in q or "system" in q):
             mock_response = {
                "thought": "User wants to update system packages. High impact action.",
                "action": "update_system",
                "param": {},
                "reply": "Preparing system update sequence..."
            }
        elif "scan" in q and "port" in q:
             mock_response = {
                "thought": "User requested port scan. This is a security action.",
                "action": "security_scan_ports",
                "param": {"target": "localhost"},
                "reply": "Initiating port scan sequence."
            }
        elif "clean" in q:
             mock_response = {
                "thought": "User wants quick clean. Initiating cleanup protocol.",
                "action": "quick_clean",
                "param": {},
                "reply": "Cleaning up temporary files and caches."
            }
        elif "update" in q: # New intent for general update
            mock_response = {
                "thought": "User wants to update something. Assuming system packages.",
                "action": "update_system",
                "param": {},
                "reply": "Checking for system updates."
            }
        elif "fix" in q or "repair" in q:
             mock_response = {
                "thought": "User wants to fix a system error. Detected missing GPG Checksum from logs.",
                "action": "fix_system_issue",
                "param": {"target": "gpg", "key_id": "EDA3E22630349F1C"},
                "reply": "Diagnosing error... Found improperly configured GPG Key. Attempting repair."
            }
        else:
             mock_response = {
                "thought": "Query not recognized as a system command. Treating as chat.",
                "action": None,
                "param": None,
                "reply": "I am standing by. How can I assist with your system today?"
            }
            
        return mock_response

    async def execute_action(self, action_data: Dict[str, Any], executor: CommandExecutor, bypass_validator: bool = False) -> Dict[str, Any]:
        """
        Executes the action decided by the Agent.
        Respects the 'Safety Layer' (Validator), unless bypass_validator is True.
        """
        action = action_data.get("action")
        
        if not action:
            return {"status": "done", "msg": ""}
            
        # 1. Validate Action (unless bypassed)
        if not bypass_validator:
            status = self.validator.validate_action(action)
            
            if status == ActionStatus.BLOCKED:
                msg = f"⛔ Security Shield Blocked Action: '{action}' is not in the allow-list."
                logger.warning(msg)
                return {"status": "blocked", "msg": msg}
                
            if status == ActionStatus.APPROVAL_NEEDED:
                impact = self.validator.get_impact_description(action)
                msg = f"⚠️ Approval Required: {impact}"
                return {"status": "approval_required", "msg": msg, "action": action, "impact": impact}

        # 2. Execute Allowed Action
        logger.info(f"Executing Action: {action}")
        
        # Dispatcher (Simple version)
        result_msg = "Action completed."
        
        if action == "system_monitor":
            result_msg = "Running full system diagnostics..." # Handled by WS stats mostly
        elif action == "security_scan_ports":
            result_msg = await executor.check_firewall()
        elif action == "simulate_attack": # Demo
            result_msg = "TRIGGERING_THREAT"
        elif action == "resolve_threat": # Demo
            result_msg = "RESOLVING_THREAT"
        elif action == "update_system":
             result_msg = await executor.update_packages()
        elif action == "fix_system_issue":
             target = action_data.get("param", {}).get("target")
             if target == "gpg":
                 key_id = action_data.get("param", {}).get("key_id")
                 result_msg = await executor.add_gpg_key(key_id)
             else:
                 result_msg = "Unknown repair target."
             
        return {"status": "done", "msg": result_msg}
