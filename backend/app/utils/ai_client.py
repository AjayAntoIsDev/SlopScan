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
    
    async def analyze_readme(
        self,
        readme_content: str,
        repo_url: str
    ) -> Dict[str, Any]:
        """
        Analyze README content using AI
        
        Args:
            readme_content: The README file content
            repo_url: The repository URL for context
            
        Returns:
            Analysis results
        """
        system_message = """You are an expert at analyzing README files and extracting key information about software projects. 
        Analyze the provided README and extract:
        1. Project purpose and description
        2. Key features and functionality
        3. Technology stack used
        4. Installation/setup requirements
        5. Usage examples if provided
        6. Project maturity indicators
        7. Code quality indicators from documentation
        
        Provide a structured analysis in JSON format."""
        
        prompt = f"""
        Analyze this README from repository: {repo_url}
        
        README Content:
        {readme_content[:8000]}  # Limit content to avoid token limits
        
        Provide analysis in JSON format with the following structure:
        {{
            "project_summary": "Brief description of what the project does",
            "key_features": ["feature1", "feature2", ...],
            "technology_stack": ["tech1", "tech2", ...],
            "setup_complexity": "simple|moderate|complex",
            "documentation_quality": "poor|fair|good|excellent",
            "project_maturity": "experimental|alpha|beta|stable|mature",
            "main_use_cases": ["use_case1", "use_case2", ...],
            "dependencies": ["dep1", "dep2", ...],
            "license": "license_type_if_mentioned"
        }}
        """
        
        try:
            response = await self.simple_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1500
            )
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw response
                return {
                    "raw_analysis": response,
                    "error": "Failed to parse JSON response"
                }
                
        except Exception as e:
            return {
                "error": f"Failed to analyze README: {str(e)}"
            }
    
    async def analyze_repository_structure(
        self,
        files: List[str],
        languages: Dict[str, int],
        repo_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze repository structure and provide insights
        
        Args:
            files: List of file paths in the repository
            languages: Dictionary of detected languages
            repo_info: Additional repository information
            
        Returns:
            Structure analysis results
        """
        system_message = """You are an expert at analyzing software project structures and identifying patterns, 
        architecture, and potential issues. Analyze the provided repository structure and provide insights."""
        
        # Limit file list to avoid token limits
        file_sample = files[:100] if len(files) > 100 else files
        
        prompt = f"""
        Analyze this repository structure:
        
        Repository: {repo_info.get('owner', 'unknown')}/{repo_info.get('repo', 'unknown')}
        Total files: {len(files)}
        Languages detected: {languages}
        
        Sample files (first 100):
        {chr(10).join(file_sample)}
        
        Provide analysis in JSON format:
        {{
            "project_type": "web_app|library|cli_tool|mobile_app|desktop_app|other",
            "architecture_pattern": "mvc|microservices|monolith|layered|other",
            "code_organization": "excellent|good|fair|poor",
            "potential_issues": ["issue1", "issue2", ...],
            "strengths": ["strength1", "strength2", ...],
            "estimated_complexity": "low|medium|high|very_high",
            "main_directories": ["dir1", "dir2", ...],
            "config_files": ["file1", "file2", ...],
            "test_coverage_indicators": "none|minimal|moderate|comprehensive"
        }}
        """
        
        try:
            response = await self.simple_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=1200
            )
            
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                return {
                    "raw_analysis": response,
                    "error": "Failed to parse JSON response"
                }
                
        except Exception as e:
            return {
                "error": f"Failed to analyze repository structure: {str(e)}"
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


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
