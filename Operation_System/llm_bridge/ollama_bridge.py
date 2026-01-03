import requests
import json
import sys
from typing import List, Dict, Any, Optional

class OllamaBridge:
    """
    Interface for Ollama API providing local LLM and Embedding services.
    Defaults to nomic-embed-text for embeddings and qwen2.5-coder:3b for generation.
    """
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.embed_model = "nomic-embed-text"
        self.gen_model = "qwen2.5-coder:3b"

    def get_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for a given text."""
        url = f"{self.host}/api/embeddings"
        payload = {
            "model": self.embed_model,
            "prompt": text
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error calling Ollama Embeddings: {e}")
            # Return empty or dummy vector if failed
            return [0.0] * 768

    def generate(self, prompt: str, system: Optional[str] = None, options: Optional[Dict] = None) -> str:
        """Generate text completion using local model."""
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.gen_model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling Ollama Generate: {e}")
            return "Ollama generation failed."

if __name__ == "__main__":
    # Fix Windows console UTF-8 encoding
    import sys
    import codecs
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    # Internal test
    bridge = OllamaBridge()
    print(f"Testing Ollama Embeddings with model: {bridge.embed_model}")
    vector = bridge.get_embeddings("Hello EVA")
    print(f"Vector size: {len(vector)} (First 5: {vector[:5]})")
    
    print(f"\nTesting Ollama Generation with model: {bridge.gen_model}")
    resp = bridge.generate("สวัสดีจ้า!")
    print(f"Response: {resp}")
