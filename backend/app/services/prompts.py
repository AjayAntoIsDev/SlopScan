import json
from typing import Dict, Any, List


class PromptTemplates:
    @staticmethod
    def readme_analysis_prompt(readme_content: str, repo_url: str) -> tuple[str, str]:
        system_message = """
        You are an expert AI text detector. Your task is to analyze the provided text and determine the probability that it was written by an AI (0-100).

        Analyze the text for human vs AI patterns as described below:

        HUMAN PATTERNS (lower AI probability 0.05-0.25):
        - Natural imperfections: typos, informal grammar, inconsistent style
        - Personal voice: use of "I think", "gonna", "pretty cool", casual contractions
        - Direct and simple language: "Added this feature", "Fixed the bug"
        - Authentic emotion: frustration or excitement: "finally got it working!", "this sucks"
        - Technical but personal tone: "had issues with X, solved by doing Y"

        AI PATTERNS (higher AI probability 0.70-0.95):
        - Perfect grammar combined with a corporate tone
        - Buzzword clusters: "comprehensive solution leveraging cutting-edge technology"
        - Marketing speak: "showcasing expertise", "seamlessly integrates", "effortlessly optimizes"
        - Structured lists with emoji bullets (e.g., ✅, 🎯, 🚀)
        - Overuse of em dashes for emphasis—like this
        - Generic and overly formal descriptions: "robust platform delivering exceptional results"

        Provide your answer as a number between 0 (definitely human) and 100 (definitely AI). return the probability and your reasoning in the following schema.
        {
        "probability": 0-100,
        "reasoning": "detailed explanation of your assessment"
        }
        """
        
        user_prompt = f"""
        Analyze this README from repository: {repo_url}
        
        README Content:
        {readme_content[:4000]}
        
        Provide your answer as a number between 0 (definitely human) and 100 (definitely AI). return the probability and your reasoning in the following schema.
        {{
        "probability": 0-100,
        "reasoning": "detailed explanation of your assessment"
        }}
        """
        
        return system_message, user_prompt

    @staticmethod
    def repository_structure_analysis_prompt(
        files: List[str],
        languages: Dict[str, int],
        repo_info: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Generate prompt for repository structure analysis
        
        Args:
            files: List of file paths in the repository
            languages: Dictionary of detected languages
            repo_info: Additional repository information
            
        Returns:
            Tuple of (system_message, user_prompt)
        """
        system_message = """You are an expert at analyzing software project structures and identifying patterns, 
        architecture, and potential issues. Analyze the provided repository structure and provide insights."""
        
        # Limit file list to avoid token limits
        file_sample = files[:100] if len(files) > 100 else files
        
        user_prompt = f"""
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
        
        return system_message, user_prompt

    @staticmethod
    def code_quality_analysis_prompt(
        code_features: Dict[str, Any],
        file_paths: List[str]
    ) -> tuple[str, str]:
        """
        Generate prompt for code quality analysis
        
        Args:
            code_features: Extracted code features from tree-sitter
            file_paths: List of analyzed file paths
            
        Returns:
            Tuple of (system_message, user_prompt)
        """
        system_message = """You are a senior software engineer expert at code quality analysis. 
        Analyze the provided code features and assess the overall code quality, patterns, and potential issues."""
        
        user_prompt = f"""
        Analyze the code quality based on these extracted features:
        
        Files analyzed: {len(file_paths)}
        Sample files: {file_paths[:20]}
        
        Code features:
        {json.dumps(code_features, indent=2)[:4000]}
        
        Provide analysis in JSON format:
        {{
            "overall_quality": "poor|fair|good|excellent",
            "code_smells": ["smell1", "smell2", ...],
            "positive_patterns": ["pattern1", "pattern2", ...],
            "complexity_assessment": "low|medium|high|very_high",
            "maintainability": "poor|fair|good|excellent",
            "naming_conventions": "inconsistent|mixed|consistent|excellent",
            "documentation_level": "none|minimal|adequate|comprehensive",
            "recommendations": ["rec1", "rec2", ...]
        }}
        """
        
        return system_message, user_prompt

    @staticmethod
    def file_selection_analysis_prompt(
        file_descriptions: List[Dict],
        repo_context: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Generate prompt for file selection analysis
        
        Args:
            file_descriptions: List of file description dictionaries
            repo_context: Repository context information
            
        Returns:
            Tuple of (system_message, user_prompt)
        """
        system_message = """You are an expert software engineer analyzing GitHub repositories to identify important source files while excluding templates, boilerplate, and auto-generated content."""
        
        languages = ", ".join(repo_context.get("languages", {}).keys())
        
        user_prompt = f"""
Analyze this GitHub repository and determine which files should be included in a selective download that excludes templates, boilerplate, auto-generated content, and other non-essential files.

Repository Context:
- Languages: {languages}
- Total files: {repo_context.get('total_files', 0)}

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
        
        return system_message, user_prompt
