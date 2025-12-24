import config
from groq import Groq
import json
import time

class LamaBrain:
    def __init__(self):
        self.api_keys = config.GROQ_API_KEYS
        self.current_key_index = 0
        self.client = self._get_client()

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "chrome_control",
                    "description": "Controls Google Chrome browser. Tab open/close/switch, history, incognito operations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum": ["new_tab", "close_tab", "reopen_tab", "next_tab", "prev_tab", "history", "downloads", "incognito", "refresh", "focus_url"],
                                "description": "Operation to perform."
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Opens an application (If only app name is provided).",
                    "parameters": {
                        "type": "object",
                        "properties": {"app_name": {"type": "string"}},
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "close_app",
                    "description": "Completely closes the application (Process Kill).",
                    "parameters": {
                        "type": "object",
                        "properties": {"app_name": {"type": "string"}},
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_running",
                    "description": "Lists running applications.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "open_website",
                    "description": "Opens a website.",
                    "parameters": {
                        "type": "object",
                        "properties": {"url": {"type": "string"}},
                        "required": ["url"]
                    }
                }
            },
             {
                "type": "function",
                "function": {
                    "name": "system_control",
                    "description": "System shutdown/restart.",
                    "parameters": {
                        "type": "object",
                        "properties": {"action": {"type": "string", "enum": ["shutdown", "restart"]}},
                        "required": ["action"]
                    }
                }
            }
        ]
        print("🧠 LAMA Brain (Chrome Expert) Started")

    def _get_client(self):
        if not self.api_keys: return None
        return Groq(api_key=self.api_keys[self.current_key_index])

    def validate_tool_call(self, tool_name, args, user_msg):
        user_msg = user_msg.lower()

        # Chrome check
        if tool_name == "chrome_control":
            # If user didn't say tab, chrome, browser etc. be suspicious (but don't block, maybe there is context)
            return True, ""

        if tool_name == "open_app":
            app = args.get("app_name", "").lower()
            if app not in user_msg and "browser" not in user_msg and "internet" not in user_msg:
                return False, f"Which app do you want me to open? (Detected: {app})"

        return True, ""

    def think(self, user_message):
        if not self.client: return "text", "API Key Error!"

        system_prompt = """You are LAMA. You are a Windows and Chrome expert.

        CHROME RULES:
        1. "Open new tab" -> chrome_control(command='new_tab')
        2. "Close tab", "close this" -> chrome_control(command='close_tab')
        3. "Open history" -> chrome_control(command='history')
        4. "Downloads" -> chrome_control(command='downloads')
        5. "Incognito" -> chrome_control(command='incognito')
        6. "Refresh", "F5" -> chrome_control(command='refresh')
        7. "Next tab", "other tab" -> chrome_control(command='next_tab')

        GENERAL RULES:
        - Never open imaginary apps (like notepad).
        - Ask if you are unsure.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            completion = self.client.chat.completions.create(
                model=config.FAST_MODEL,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1024,
                temperature=0.1
            )

            response_msg = completion.choices[0].message

            if response_msg.tool_calls:
                tool_call = response_msg.tool_calls[0]
                function_name = tool_call.function.name

                try:
                    function_args = json.loads(tool_call.function.arguments)
                except:
                    return "text", "Technical error while processing command."

                is_valid, error_msg = self.validate_tool_call(function_name, function_args, user_message)
                if not is_valid:
                    return "text", error_msg

                return "tool_call", {"name": function_name, "args": function_args}

            return "text", response_msg.content

        except Exception as e:
            return "text", f"Error: {str(e)}"
