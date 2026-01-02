import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env if exists (even if blocked by gitignore, python-dotenv can read it if we provide path)
load_dotenv()

class ToolCall:
    """Standardized tool call object"""
    def __init__(self, name: str, args: Dict[str, Any]):
        self.name = name
        self.args = args

class LLMResponse:
    """Standardized LLM response object"""
    def __init__(self, text: str = "", tool_calls: List[ToolCall] = None, usage: Dict = None):
        self.text = text
        self.tool_calls = tool_calls or []
        self.usage = usage or {"input_tokens": 0, "output_tokens": 0}

class LLMBridge:
    """
    Real Gemini API Bridge for EVA 8.1.0
    Supports Dual-Phase One-Inference with Function Calling.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "AIzaSyBdwmQpGEbiGxM7rOsC7NEKh1wfj8YqtXY")
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.conversation_history = []
        self.chat_session = None
        
        # Tools will be bound during generate call
        self.tools = []

    def _initialize_chat(self, tools: Optional[List[Dict]] = None):
        """Initialize or re-initialize chat session with tools."""
        # Convert tool dicts to genai.types.FunctionDeclaration if needed
        # For simplicity, we use the dict format which genai supports
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=tools
        )
        self.chat_session = self.model.start_chat(history=[])

    def _to_dict(self, obj: Any) -> Any:
        """Simple convert objects to standard Python types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._to_dict(x) for x in obj]
        elif hasattr(obj, "to_dict"):
            # Don't recurse deep into to_dict
            try: return obj.to_dict()
            except: return str(obj)
        # For Gemini SDK types, often they can be converted to dict simply
        try:
            return dict(obj)
        except:
            return str(obj)

    def generate(
        self,
        prompt: str,
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """
        Generate Gemini response with optional function calling.
        """
        if not self.chat_session or tools != self.tools:
            self.tools = tools
            self._initialize_chat(tools)

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            response = self.chat_session.send_message(prompt, generation_config=generation_config)
            
            # Process response and ensure serializable content
            text = ""
            tool_calls = []
            
            # Safe text/tool extraction
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        text += part.text
                    if part.function_call:
                        # Simple conversion to avoid recursion
                        args = {k: v for k, v in part.function_call.args.items()}
                        tool_calls.append(ToolCall(
                            name=part.function_call.name,
                            args=args
                        ))

            return LLMResponse(
                text=text,
                tool_calls=tool_calls,
                usage={"input_tokens": 0, "output_tokens": 0}
            )

        except Exception as e:
            print(f"Error in Gemini Generate: {e}")
            return LLMResponse(text=f"Error: {str(e)}")

    def continue_with_result(self, function_result: str, function_name: str = "sync_biocognitive_state") -> LLMResponse:
        """
        Continue LLM inference after function call (Phase 2).
        """
        if not self.chat_session:
            return LLMResponse(text="Error: No active chat session to continue.")

        try:
            # Safer way to deliver function response: send as part of a content object
            # For Gemini 2.0, the chat session manages the history
            response = self.chat_session.send_message({
                "role": "user",
                "parts": [{
                    "function_response": {
                        "name": function_name,
                        "response": {"result": function_result}
                    }
                }]
            })
            
            # Safe text extraction
            final_text = ""
            if hasattr(response, "candidates") and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        final_text += part.text
            elif hasattr(response, "text"):
                final_text = response.text
                
            return LLMResponse(text=final_text or "[Empty Response]")

        except Exception as e:
            print(f"Error in Gemini Continue: {e}")
            # Fallback
            try:
                response = self.chat_session.send_message(f"[System: Function {function_name} returned {function_result}. Please continue reasoning.]")
                return LLMResponse(text=response.text if hasattr(response, 'text') else str(response))
            except:
                return LLMResponse(text=f"Error: {str(e)}")

    def get_token_usage(self) -> Dict[str, int]:
        """Compatibility method for token usage."""
        return {"total_tokens": 0, "estimated_cost": 0.0}

    def get_conversation_history(self) -> List[Dict]:
        """Compatibility method for conversation history."""
        return []

    def reset(self):
        """Reset session."""
        self.chat_session = None

# Tool definition for sync_biocognitive_state
SYNC_BIOCOGNITIVE_STATE_TOOL = {
    "name": "sync_biocognitive_state",
    "description": """
    Synchronize biological and cognitive state based on stimulus analysis.

    This function triggers:
    1. PhysioController to update body state (hormones, ANS)
    2. HeptStreamRAG to retrieve emotion-congruent memories
    3. CIN to build Phase 2 context with embodied sensation

    Call this function ALWAYS after analyzing user input in Phase 1.
    """,
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "stimulus_vector": {
                "type": "OBJECT",
                "description": "Stimulus intensity across dimensions (0.0-1.0)",
                "properties": {
                    "stress": {"type": "NUMBER", "description": "Stress/threat level"},
                    "warmth": {"type": "NUMBER", "description": "Social warmth/affection"},
                    "arousal": {"type": "NUMBER", "description": "Physiological arousal"},
                    "valence": {"type": "NUMBER", "description": "Emotional valence (negative-positive)"}
                },
                "required": ["stress", "warmth", "arousal", "valence"]
            },
            "tags": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Semantic tags for memory retrieval (e.g. ['gratitude', 'longing'])"
            }
        },
        "required": ["stimulus_vector", "tags"]
    }
}

if __name__ == "__main__":
    # Fix Windows console UTF-8 encoding
    import sys
    import codecs
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("=== Testing Real Gemini Bridge ===\n")
    llm = LLMBridge()
    
    # Test a simple prompt
    resp = llm.generate("Hello, who are you?")
    print(f"Gemini: {resp.text}")
