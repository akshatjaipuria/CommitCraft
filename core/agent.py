import os
import anyio
import json
import re
from google import genai
from services.git_tools import tools_map
from core.logger import log_event
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

SYSTEM_PROMPT = """You are a professional Git Commit Agent. Your goal is to write a high-quality, conventional commit message based on repository changes.

AVAILABLE TOOLS:
- get_staged_diff: Retrieves the diff of staged changes.
- get_commit_context: Retrieves the last 5 commit messages for style reference.
- get_git_status: Retrieves current branch and status of files.

RESPONSE FORMAT:
You MUST respond in JSON format ONLY. 
- To use a tool: {"tool_name": "name", "tool_arguments": {}}
- To provide the final answer: {"answer": "your commit message", "reasoning": "explanation"}
"""

class CommitAgent:
    """
    The core agentic engine that handles iterative reasoning for commit generation.
    Supports both Stateful (API-managed) and Stateless (Manual-managed) loop strategies.
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview"

    def parse_response(self, text: str) -> dict:
        """
        Cleans and parses the LLM's raw text response into a Python dictionary.
        Handles markdown blocks and extraction of JSON structures.
        """
        text = text.strip()
        try:
            # Strip markdown JSON wrappers if present
            clean_text = re.sub(r'```json\s*|\s*```', '', text)
            start = clean_text.find('{')
            end = clean_text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = clean_text[start:end+1]
                return json.loads(json_str)
            return json.loads(clean_text)
        except Exception as e:
            raise ValueError(f"JSON Parsing Error: {str(e)} | Raw Output: {text[:200]}")

    async def run(self, query: str, repo_path: str, mode: str = "stateful"):
        """
        Primary entry point for the agent.
        
        Args:
            query: User's custom instructions
            repo_path: Path to the local git repo
            mode: 'stateful' or 'stateless'
        """
        log_event("SESSION_START", {"mode": mode, "path": repo_path})
        
        if mode == "stateless":
            return await self._run_stateless_loop(query, repo_path)
        return await self._run_stateful_loop(query, repo_path)

    async def _run_stateless_loop(self, query: str, repo_path: str):
        """
        Iterative loop using 'Normal Calls'. 
        Manually concatenates conversation history into a single prompt for each turn.
        """
        ui_history = []
        history_buffer = f"USER_QUERY: {query}\nREPO_PATH: {repo_path}\n"
        
        # Safety limit of 10 iterations to prevent infinite loops while allowing deep reasoning
        for i in range(10):
            full_prompt = f"{SYSTEM_PROMPT}\n\nCONVERSATION HISTORY:\n{history_buffer}"
            
            try:
                log_event("STATELESS_LOOP_STEP", i + 1)
                log_event("STATELESS_PROMPT", full_prompt)
                
                # Offload blocking API call to background thread
                response = await anyio.to_thread.run_sync(
                    lambda: self.client.models.generate_content(model=self.model_id, contents=full_prompt)
                )
                parsed = self.parse_response(response.text)
            except Exception as e:
                return self._handle_error(f"Stateless Loop Error: {str(e)}", ui_history)

            # If the model provides an 'answer', it has finished its reasoning
            if "answer" in parsed:
                return self._handle_final_answer(parsed, ui_history, "stateless")

            # If the model requests a tool, we execute it and continue the loop
            if "tool_name" in parsed:
                result_str = await self._execute_tool(parsed["tool_name"], repo_path, ui_history)
                history_buffer += f"\nModel Requested: {parsed['tool_name']}\nTool Output: {result_str}\n"
            else:
                history_buffer += "\nError: Response missing 'answer' or 'tool_name'.\n"

        return self._handle_error("Agent reached maximum safety iteration limit (10).", ui_history)

    async def _run_stateful_loop(self, query: str, repo_path: str):
        """
        Iterative loop using 'Chat Sessions'.
        The API manages the context window and conversation history internally.
        """
        chat = self.client.chats.create(model=self.model_id)
        ui_history = []
        current_input = f"{SYSTEM_PROMPT}\n\nUSER_QUERY: {query}\nREPO_PATH: {repo_path}"
        
        # Safety limit of 10 iterations to prevent infinite loops while allowing deep reasoning
        for i in range(10):
            try:
                log_event("STATEFUL_LOOP_STEP", i + 1)
                response = await anyio.to_thread.run_sync(lambda: chat.send_message(current_input))
                parsed = self.parse_response(response.text)
            except Exception as e:
                return self._handle_error(f"Stateful Loop Error: {str(e)}", ui_history)

            # If the model provides an 'answer', it has finished its reasoning
            if "answer" in parsed:
                return self._handle_final_answer(parsed, ui_history, "stateful")

            # If the model requests a tool, we execute it and continue the loop
            if "tool_name" in parsed:
                result_str = await self._execute_tool(parsed["tool_name"], repo_path, ui_history)
                current_input = f"TOOL_RESULT for {parsed['tool_name']}: {result_str}"
            else:
                current_query = "Error: Your response did not contain an 'answer' or a 'tool_name'. Please provide one in JSON format."

        return self._handle_error("Agent reached maximum safety iteration limit (10).", ui_history)

    async def _execute_tool(self, t_name: str, repo_path: str, ui_history: list) -> str:
        """Helper to execute a tool and log full results for transparency."""
        log_event("TOOL_CALL", t_name)
        tool_func = tools_map.get(t_name, lambda **kwargs: "Error: Tool not found.")
        
        result_str = await anyio.to_thread.run_sync(lambda: tool_func(repo_path=repo_path))
        
        ui_history.append({"type": "tool", "name": t_name, "status": "Success"})
        # Log the full result content so it's visible in agent.log
        log_event("TOOL_RESULT", {"name": t_name, "data": result_str})
        return result_str

    def _handle_final_answer(self, parsed: dict, ui_history: list, mode: str):
        """Helper to format the final successful response."""
        ans = parsed["answer"]
        log_event("FINAL_ANSWER", ans)
        return {
            "result": ans, 
            "reasoning": parsed.get("reasoning", ""), 
            "history": ui_history,
            "mode": mode
        }

    def _handle_error(self, message: str, ui_history: list):
        """Helper to format error responses."""
        log_event("ERROR", message)
        return {"error": message, "history": ui_history}
