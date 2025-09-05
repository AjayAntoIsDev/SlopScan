"""
AI Client utility for Hack Club AI service
Provides a simple interface for sending prompts and getting responses
"""
import httpx
from typing import Optional, Dict, Any, List
import json
from app.config import settings


class HackClubAIClient:
    """Client for interacting with Hack Club AI service"""
    
    def __init__(self):
        self.base_url = "https://ai.hackclub.com"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to Hack Club AI
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use for completion
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dict containing the AI response
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error occurred: {e}")
        except Exception as e:
            raise Exception(f"Error in AI request: {e}")
    
    async def simple_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a simple prompt and get the response content
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to set context
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            The AI response content as a string
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract content from response
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise Exception("No response content found")
                
        except Exception as e:
            raise Exception(f"Error in simple prompt: {e}")
    

# Singleton instance
_ai_client: Optional[HackClubAIClient] = None

def get_ai_client() -> HackClubAIClient:
    """Get or create the AI client singleton"""
    global _ai_client
    if _ai_client is None:
        _ai_client = HackClubAIClient()
    return _ai_client

async def cleanup_ai_client():
    """Cleanup the AI client"""
    global _ai_client
    if _ai_client:
        await _ai_client.close()
        _ai_client = None
