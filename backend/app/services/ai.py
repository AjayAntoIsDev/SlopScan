import httpx
import json
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models import FileInfo
from app.services.prompts import PromptTemplates


class HackClubAIClient:
    
    def __init__(self):
        self.base_url = "https://ai.hackclub.com"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "qwen/qwen3-32b",
        temperature: float = 0.6,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
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
    
    async def prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: str = "qwen/qwen3-32b",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
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
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                raise Exception("No response content found")
                
        except Exception as e:
            raise Exception(f"Error in prompt: {e}")
    
    async def close(self):
        await self.client.aclose()


class AIService:    
    def __init__(self):
        self.client = HackClubAIClient()
    
    async def analyze_files_for_selection(self, files: List[FileInfo], repo_context: Dict[str, Any]) -> Dict[str, Any]:
        file_descriptions = []
        for file_info in files:
            file_descriptions.append({
                "path": file_info.path,
                "name": file_info.name,
                "size": file_info.size,
                "is_template": getattr(file_info, 'is_template', False),
                "is_auto_generated": getattr(file_info, 'is_auto_generated', False)
            })
        
        system_message, user_prompt = PromptTemplates.file_selection_analysis_prompt(
            file_descriptions, repo_context
        )
        
        try:
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.1,
                max_tokens=4000
            )
            
            ai_analysis = json.loads(response)
            
            selected_files = []
            excluded_files = []
            
            for file_info in files:
                file_decision = next((f for f in ai_analysis["files"] if f["path"] == file_info.path), None)
                
                if file_decision:
                    file_info.ai_confidence = file_decision.get("confidence", 0.5)
                    file_info.reason = file_decision.get("reason", "")
                    
                    if file_decision["include"]:
                        selected_files.append(file_info)
                    else:
                        excluded_files.append(file_info)
                else:
                    if not getattr(file_info, 'is_template', False) and not getattr(file_info, 'is_auto_generated', False):
                        selected_files.append(file_info)
                    else:
                        excluded_files.append(file_info)
            
            return {
                "selected_files": selected_files,
                "excluded_files": excluded_files,
                "analysis_summary": ai_analysis.get("summary", {}),
                "total_selected": len(selected_files),
                "total_excluded": len(excluded_files)
            }
            
        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
    
    async def analyze_readme(self, readme_content: str, repo_url: str) -> Dict[str, Any]:
        system_message, user_prompt = PromptTemplates.readme_analysis_prompt(
            readme_content, repo_url
        )
        
        try:
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=3000
            )
            
            return self._parse_json_response(response)
                
        except Exception as e:
            return {
                "error": f"Failed to analyze README: {str(e)}"
            }
    
    async def analyze_commits(
        self,
        commits_data: List[Dict[str, Any]],
        repo_info: Dict[str, Any],
        readme_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            total_commits = repo_info.get('total_commits', len(commits_data))
            
            readme = readme_analysis or {}
            
            system_message, user_prompt = PromptTemplates.commits_analysis_prompt(
                total_commits=total_commits,
                readme=readme,
                commits_data=commits_data,
                repo_info=repo_info
            )
            
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.3, 
                max_tokens=2000
            )
            
            ai_analysis = self._parse_json_response(response)
            
            if "error" in ai_analysis:
                return {
                    "total_commits_analyzed": len(commits_data),
                    "repo_info": repo_info,
                    "error": ai_analysis["error"],
                    "raw_response": ai_analysis.get("raw_analysis", response)
                }
            
            ai_analysis.update({
                "total_commits_analyzed": len(commits_data),
                "total_commits_in_repo": total_commits,
                "repo_info": repo_info,
                "analysis_timestamp": "analyzed",
                "status": "completed"
            })
            
            return ai_analysis
            
        except Exception as e:
            return {
                "total_commits_analyzed": len(commits_data),
                "repo_info": repo_info,
                "error": f"Failed to analyze commits: {str(e)}",
                "status": "failed"
            }

    async def analyze_som(
        self,
        project_data: Dict[str, Any],
        repo_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            devlogs = project_data.get("devlogs", [])
            som_info = {
                "title": project_data.get("title"),
                "description": project_data.get("description"),
                "devlogs_count": len(devlogs),
                "devlogs": devlogs
            }
            
            commits_data = []
            total_commits = 0
            readme = {}
            
            if repo_analysis:
                commits_data = repo_analysis.get("commits", [])
                total_commits = repo_analysis.get("total_commits", 0)
                readme = repo_analysis.get("readme_analysis", {})
            
            system_message, user_prompt = PromptTemplates.som_analysis_prompt(
                readme=readme,
                total_commits=total_commits,
                commits_data=commits_data,
                som_info=som_info
            )
            
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=3000
            )
            
            ai_analysis = self._parse_json_response(response)
            
            if "error" in ai_analysis:
                return {
                    "project_title": som_info["title"],
                    "total_devlogs": len(devlogs),
                    "has_repo_analysis": repo_analysis is not None,
                    "error": ai_analysis["error"],
                    "raw_response": ai_analysis.get("raw_analysis", response)
                }
            
            ai_analysis.update({
                "project_title": som_info["title"],
                "total_devlogs": len(devlogs),
                "has_repo_analysis": repo_analysis is not None,
                "analysis_timestamp": "analyzed",
                "status": "completed"
            })
            
            return ai_analysis
            
        except Exception as e:
            return {
                "project_title": project_data.get("title", "Unknown"),
                "total_devlogs": len(project_data.get("devlogs", [])),
                "has_repo_analysis": repo_analysis is not None,
                "error": f"Failed to analyze Summer of Making project: {str(e)}",
                "status": "failed"
            }

    async def select_files_for_analysis(
        self,
        readme_analysis: Dict[str, Any],
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            system_message, user_prompt = PromptTemplates.file_selection(
                readme_analysis, structure, max_files=20
            )
            
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.2,
                max_tokens=2000
            )
            
            ai_analysis = self._parse_json_response(response)
            
            if "error" in ai_analysis:
                return {
                    "selected_files": [],
                    "error": ai_analysis["error"],
                    "raw_response": ai_analysis.get("raw_analysis", response)
                }
            
            return {
                "selected_files": ai_analysis.get("selected_files", []),
                "total_selected": len(ai_analysis.get("selected_files", [])),
            }
            
        except Exception as e:
            return {
                "selected_files": [],
                "error": f"Failed to select files for analysis: {str(e)}",
                "status": "failed"
            }

    async def analyze_code(
        self,
        code_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            system_message, user_prompt = PromptTemplates.code_analysis_prompt(
                code_features
            )
            
            response = await self.client.prompt(
                prompt=user_prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=6000
            )
            
            ai_analysis = self._parse_json_response(response)
            print(ai_analysis)
            
            if "error" in ai_analysis:
                return {
                    "total_files_analyzed": len(code_features),
                    "error": ai_analysis["error"],
                    "raw_response": ai_analysis.get("raw_analysis", response)
                }
            
            return {
                "total_files_analyzed": len(code_features),
                "analysis_results": ai_analysis
            }
            
        except Exception as e:
            return {
                "total_files_analyzed": len(code_features),
                "error": f"Failed to analyze code features: {str(e)}",
                "status": "failed"
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        cleaned_response = response.strip()
        
        import re
        think_pattern = r'<think>.*?</think>'
        cleaned_response = re.sub(think_pattern, '', cleaned_response, flags=re.DOTALL).strip()
        
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:] 
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]  
        
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  

        cleaned_response = cleaned_response.strip()
        
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            return {
                "raw_analysis": response,
                "cleaned_response": cleaned_response,
                "error": f"Failed to parse JSON response: {str(e)}"
            }

_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

async def cleanup_ai_service():
    global _ai_service
    if _ai_service:
        await _ai_service.client.close()
        _ai_service = None
