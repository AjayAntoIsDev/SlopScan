"""
AI service for intelligent file analysis and selection using Groq
"""
import json
from typing import List, Dict, Any, Optional
from groq import Groq
import structlog

from app.config import settings
from app.models import FileInfo

logger = structlog.get_logger()


class AIService:
    """Service for AI-powered file analysis using Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
    
    async def analyze_files_for_selection(self, files: List[FileInfo], repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to intelligently select files that are important and exclude templates/auto-generated content
        """
        # Prepare file list for AI analysis
        file_descriptions = []
        for file_info in files:
            file_descriptions.append({
                "path": file_info.path,
                "name": file_info.name,
                "size": file_info.size,
                "is_template": file_info.is_template,
                "is_auto_generated": file_info.is_auto_generated
            })
        
        # Create prompt for AI analysis
        prompt = self._create_analysis_prompt(file_descriptions, repo_context)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Groq's fast model
                messages=[
                    {"role": "system", "content": "You are an expert software engineer analyzing GitHub repositories to identify important source files while excluding templates, boilerplate, and auto-generated content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            # Apply AI decisions to files
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
                    # Default behavior for files not analyzed by AI
                    if not file_info.is_template and not file_info.is_auto_generated:
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
            logger.error("AI analysis failed", error=str(e))
            # Fallback to rule-based selection
            return self._fallback_selection(files)
    
    def _create_analysis_prompt(self, file_descriptions: List[Dict], repo_context: Dict[str, Any]) -> str:
        """Create a detailed prompt for AI analysis"""
        languages = ", ".join(repo_context.get("languages", {}).keys())
        
        prompt = f"""
Analyze this GitHub repository and determine which files should be included in a selective download that excludes templates, boilerplate, auto-generated content, and other non-essential files.

Repository Context:
- Languages: {languages}
- Total files: {repo_context.get('total_files', 0)}
- File types: {json.dumps(repo_context.get('file_types', {}), indent=2)}

Files to analyze:
{json.dumps(file_descriptions, indent=2)}

Please provide your analysis in this exact JSON format:
{{
    "summary": {{
        "primary_language": "detected primary programming language",
        "project_type": "web app/library/tool/etc",
        "architecture_pattern": "MVC/microservices/monolith/etc",
        "key_insights": ["insight1", "insight2"]
    }},
    "files": [
        {{
            "path": "exact file path",
            "include": true/false,
            "confidence": 0.0-1.0,
            "reason": "detailed reason for inclusion/exclusion"
        }}
    ]
}}

Focus on including:
- Core source code files
- Important configuration files (package.json, requirements.txt, etc.)
- Key documentation (README, API docs)
- Essential build files (Dockerfile, Makefile)
- Database schemas and migrations

Exclude:
- Test files and test data
- Build artifacts and compiled files
- Auto-generated code (protobuf, swagger, etc.)
- Template and boilerplate files
- IDE configuration files
- Dependency lock files (unless critical)
- Log files and temporary files
- Examples and samples (unless they're the main purpose)

Be selective and prioritize files that demonstrate the actual implementation and architecture.
"""
        return prompt
    
    def _fallback_selection(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Fallback rule-based selection when AI fails"""
        selected_files = []
        excluded_files = []
        
        important_files = {
            'README.md', 'README.txt', 'readme.md', 'readme.txt',
            'package.json', 'requirements.txt', 'Pipfile', 'pyproject.toml',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'Dockerfile', 'docker-compose.yml', 'Makefile',
            'main.py', 'app.py', 'index.js', 'main.js', 'server.js'
        }
        
        for file_info in files:
            # Always include important configuration and entry point files
            if file_info.name in important_files:
                file_info.reason = "Important configuration or entry point file"
                file_info.ai_confidence = 0.9
                selected_files.append(file_info)
            # Include source files that aren't templates or auto-generated
            elif not file_info.is_template and not file_info.is_auto_generated:
                ext = '.' + file_info.name.split('.')[-1] if '.' in file_info.name else ''
                if ext in settings.allowed_extensions_list:
                    file_info.reason = "Source code file"
                    file_info.ai_confidence = 0.7
                    selected_files.append(file_info)
                else:
                    file_info.reason = "Non-source file type"
                    excluded_files.append(file_info)
            else:
                file_info.reason = "Template or auto-generated file"
                excluded_files.append(file_info)
        
        return {
            "selected_files": selected_files,
            "excluded_files": excluded_files,
            "analysis_summary": {
                "method": "rule-based_fallback",
                "note": "AI analysis unavailable, used rule-based selection"
            },
            "total_selected": len(selected_files),
            "total_excluded": len(excluded_files)
        }
