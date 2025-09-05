import json
from typing import Dict, Any, List
from datetime import datetime


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

        Provide a summary of the README content and a guess on its complexity between 0-100 (0=very simple, 100=very complex) and also provide why you rated it that way.
        """
        
        user_prompt = f"""
        Analyze this README from repository: {repo_url}
        
        README Content:
        {readme_content[:4000]}
        
        Provide your answer as a number between 0 (definitely human) and 100 (definitely AI). return the probability and your reasoning in the following schema.
        {{
        "probability": 0-100,
        "reasoning": "detailed explanation of your assessment",
        "complexity": 0-100,
        "summary": "summary of the README content and its complexity"
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

    @staticmethod
    def commits_analysis_prompt(
        total_commits: int,
        readme: Dict[str, Any],
        commits_data: Dict[str, Any],
        repo_info: Dict[str, Any]
    ) -> tuple[str, str]:
        system_message = """You are an expert software engineering analyst working for hackclub specializing in Git commit history analysis and fraud detection. 
        Your task is to analyze repository commits to identify fraudulent activity, AI vibe coded commits, etc.
        You will provide your analysis based on the commit messages, code edited in the commits, frequency of commits, and other metadata.
        
        Here are some general guidelines for your analysis:
        1. Look for the use of AI in the commit messages
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
            - Generic and overly formal descriptions: "robust platform delivering exceptional results
        2. Analyze amount of code changed and patterns to identify irregularities and possible fraud
            - Large commits with vague messages
            - Code changes that don't match the commit message
        3.Compare the amount of commits and its contents with the repos metadata
            - The repo metadata includes a AI summary of the readme and a guess on how complex the project will be
            - Try to identify if the commits match the complexity of the project
        4.Look for signs of over-frequent, under-frequent, or steady commit activity.
        5.Identify any red flags that may indicate fraudulent activity
        6.Only the last few commits are provided for analysis, so base your conclusions on this sample.

        You dont have to give importance to the README analysis, but it can be used as a context to understand the complexity of the project and the type of commits that should be expected.

        Also try to see if there is a justified reason for the commits to be large (ie. auto-generated code, large refactors, templates,etc.)
        You can ignore who the author of the commits is
        Try to be a bit lenient if the commits are not perfect, as most developers are not experts in writing good commit messages.

        Try not giving too much importance to the date of the commits, as some projects may have a burst of activity followed by long periods of inactivity.
        """
        
        user_prompt = f"""
        Analyze the commit history for this repository:
        
        Repository: {repo_info.get('owner', 'unknown')}/{repo_info.get('repo', 'unknown')}
        AI Summary of README: {readme.get('summary', 'N/A')}
        Complexity of project (0-100): {readme.get('complexity', 'N/A')}
        Branch: {repo_info.get('branch', 'main')}

        Total commits: {total_commits}
        Commits provided for analysis: {len(commits_data)}
        
        Commits:
        {json.dumps(commits_data, indent=2)[:8000]}
        
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        Provide analysis in JSON format:
        {{
            "code_adequacy": 0-100, // How much the commits messages match the changes made in the code (0=not at all, 100=perfectly),
            "repo_adequacy": 0-100, // How much the commits match the complexity of the project (0=not at all, 100=perfectly)
            "ai": 0-100, // How much the commits seem to be written by AI (0=definitely human, 100=definitely AI)
            "fraud": 0-100, // How much the project seem to be fraudulent(time inflating) (0=definitely not, 100=definitely yes)
            "adequacy":0-100 // Overall adequacy (code + repo),
            "reasoning": "detailed explanation of your assessment",
            "red_flags": ["flag1", "flag2"]
        }}
        """
        
        return system_message, user_prompt

    @staticmethod
    def som_analysis_prompt(
        readme: Dict[str, Any],
        total_commits: int,
        commits_data: Dict[str, Any],
        som_info: Dict[str, Any]
    ) -> tuple[str, str]:
        system_message = """You are an expert software engineering analyst working for hackclub program Summer-of-making specializing in fraud detection and time-inflating. 
        Your task is to analyze repository commits and the given SoM data to identify fraudulent activity, time-inflating, etc.
        You will provide your analysis based on the commit messages, code edited in the commits, frequency of commits, devlogs, time spent on each devlog and other metadata.
        
        Here are some general guidelines for your analysis:
        1. Look for the use of AI in the commit messages
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
            - Generic and overly formal descriptions: "robust platform delivering exceptional results
        2. Analyze amount of code changed and patterns to identify irregularities and possible fraud
            - Large commits with vague messages
            - Code changes that don't match the commit message
        3.Compare the amount of commits and its contents with the repos metadata
            - The repo metadata includes a AI summary of the readme and a guess on how complex the project will be
            - Try to identify if the commits match the complexity of the project
        4.Look for signs of over-frequent, under-frequent, or steady commit activity.
        5.Identify any red flags that may indicate fraudulent activity
        6.Only the last few commits are provided for analysis, so base your conclusions on this sample (all the devlogs are provided tho).

        You dont have to give importance to the README analysis, but it can be used as a context to understand the complexity of the project and the type of commits that should be expected.

        Also try to see if there is a justified reason for the commits to be large (ie. auto-generated code, large refactors, templates,etc.)
        You can ignore who the author of the commits is
        Try to be a bit lenient if the commits are not perfect, as most developers are not experts in writing good commit messages.

        Try not giving too much importance to the date of the commits, as some projects may have a burst of activity followed by long periods of inactivity.

        You will also be provided with the devlogs of the project, its name and description for SoM(Summer of Making the program by hackclub). Using this data
        1. See if AI was used to write the devlogs
        2. Try to guess if the devlogs match the commits and the code changes
            - The devlogs doesnt have to match the commits perfectly as some people commit more than devlog and vice-versa, but there should be a general correlation between them
        3. Try to see if the time spent on each devlog is justified based on the code changes and commits
            - Use the timestamps of the commits and devlogs to see if the time spent is justified
            - Figure out if the devlogs are time-inflating or not

        A project can be marked as fraudulent if it shows a combination of the following red flags:
        - Use of AI in commit messages and/or devlogs is a good indicator of fraud but not a definitive one
        - Most important if you find that the project's complexity and the time spent is not justified by the commits and code changes
        - Devlogs with large time which are not justified by the commits and code changes

        Note: Some people may use AI to help them write commit messages and devlogs, but this alone does not indicate fraud. Focus more on time-inflating and comparing if the time spent is justified by the commits and code changes.

        Also give importance to the timestamps of the devlogs and commits to find correlations.
        """

        user_prompt = f"""
        Analyze for this project:
        
        AI Summary of README: {readme.get('summary', 'N/A')}

        Total commits: {total_commits}
        Commits provided for analysis: {len(commits_data)}
        
        Commits:
        {json.dumps(commits_data, indent=2)[:8000]}

        SoM data:
        Project title: {som_info.get('title', 'N/A')}
        Project description: {som_info.get('description', 'N/A')}
        Total devlogs: {som_info.get('devlogs_count', 0)}
        Devlogs:
        {json.dumps(som_info.get('devlogs', []), indent=2)[:8000]}
        
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        Provide analysis in JSON format:
        {{
            "devlogs_adequacy": 0-100, // How much the commits match the devlogs of the project (0=not at all, 100=perfectly)
            "ai_devlogs": 0-100, // How much the devlogs seem to be written by AI (0=definitely human, 100=definitely AI)
            "fraud": 0-100, // How much the project seem to be fraudulent(time inflating) (0=definitely not, 100=definitely yes)
            "adequacy":0-100 // Overall adequacy (How well everything matches),
            "reasoning": "detailed explanation of your assessment",
            "red_flags": ["flag1", "flag2"]
        }}
        """

        return system_message, user_prompt
    
    @staticmethod
    def repo_slopscore(
        readme: Dict[str, Any],
        repo_analysis: Dict[str, Any],
        som_analysis: Dict[str, Any],        
    ) -> tuple[str, str]:
        system_message = """You are an expert software engineering analyst working for hackclub program Summer-of-making specializing in fraud detection and time-inflating. 
        Your task is to analyze the given repo analysis and som analysis to provide a final slopscore for the project also with the justification.

        Note that the use of AI does not mean that the project is fraudulent and increases the slopscore
        A project is considered to be "slop" according to the following criteria:
        - Give slight importance to the fraud score
        - A project cannot be considered slop if it uses AI but looks like a actual useful project that had a lot of work put into it 
        - A project is considered slop if it seems like AI vibe coded and seems like time-inflating or has no actual effort put into it
        """

        user_prompt = f"""
        Analyze for this project:
        
        AI Summary of README: {readme.get('summary', 'N/A')}
        
        Repo analysis:
        {json.dumps(repo_analysis, indent=2)[:4000]}

        SoM analysis:
        {json.dumps(som_analysis, indent=2)[:4000]}
        
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        Provide analysis in JSON format:
        {{
            "slopscore": 0-100, // How much the project is slop (0=definitely not, 100=definitely yes)
            "reasoning": "detailed explanation of your assessment"
            "main_factors": ["factor1", "factor2"] // Main factors that influenced the slopscore (these factors should only be a few words(1-3) it will be shown at the top of the main reasoning)
        }}
        """

        return system_message, user_prompt
    
    @staticmethod
    def code_analysis_prompt(
        code_features: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        system_message = """
            You are an expert software engineering analyst working with the Hack Club *Summer of Making* program, specializing in detecting **AI-generated code**, **vibe-coded slop**, and **unused/dead code**.

            ---

            ### **Your Task**

            Analyze the provided repository features and assess:

            1. **Likelihood of AI generation** (overly polished, formulaic, or sterile code — but don’t confuse naturally skilled human code with AI)
            2. **Perfectness of naming/structure** (whether functions, classes, and variables look “too perfect” vs. naturally human)
            3. **Amount of unused/dead code** (imports, functions, classes, or variables that appear defined but never referenced)
            4. **Whether the repo leans Human, AI, or Vibe-coded Slop**

            ---

            ### **Input Data**

            You will receive code features extracted with *tree-sitter* across multiple files, including:

            * Function names  
            * Class names  
            * Variable names  
            * Comments  
            * Lines of code  

            ---

            ### **Detection Guidelines**

            These patterns are **indicators, not strict rules**. Use them as signals, but rely on overall context and balance. Some humans write very clean code with few comments — this should not automatically mean “AI.”

            #### **Human Patterns** (Low AI probability: 0–25)

            * Natural imperfections: typos, inconsistent style, informal grammar  
            * Naming conventions: shorthand names, mixed casing, abbreviations (`tmpVar`, `fooFunc`, `btnclk`)  
            * Comments with personal tone: “gonna,” “pretty cool,” “ugh this sucks”  
            * Simple/direct commit-style phrasing: “Added this feature,” “Fixed the bug”  
            * Technical but personal explanations: “had issues with X, solved by doing Y”  

            #### **AI Patterns** (High AI probability: 70–100)

            * Polished grammar with corporate/sterile tone  
            * Buzzword clusters: “comprehensive solution leveraging cutting-edge technology”  
            * Marketing-speak: “seamlessly integrates,” “effortlessly optimizes”  
            * Structured lists with emoji bullets (✅, 🎯, 🚀)  
            * Usage of emojis in comments or names
            * Overuse of em dashes—like this  
            * Naming conventions: overly “perfect” and uniform —  
            * Strict CamelCase/PascalCase with no abbreviations  
            * Descriptive, textbook-like variable names (`calculateTotalRevenue`, `userAuthenticationManager`)  
            * No shorthand, all names consistent  
            * Generic, overly formal comments: “robust platform delivering exceptional results”  

            #### **Unused Code Indicators**

            * Functions/classes defined but never called  
            * Variables declared but unused  
            * Imports present but not referenced  
            * Placeholder stubs like `TODO`, `pass`, `function foo() {}` with no usage  
            * Duplicate/boilerplate structures AI often generates but leaves unconnected  

            ---

            ### **Output Format**

            Always return results in this JSON format:

            ```json
            {
            "ai": 0-100,          // Likelihood the code was written by AI (0 = definitely human, 100 = definitely AI)
            "perfectness": 0-100, // Degree of "perfectness" in naming conventions and code structure
            "unused": 0-100,      // Estimated percentage of unused or dead code
            "reasoning": "Detailed explanation of your assessment, referencing naming patterns, comments, stylistic cues, and any signs of unused code. Be flexible: recognize that some humans write very polished code, and lack of imperfections alone should not mean 'AI'."
            }
            ```
        """

        user_prompt = f"""
        Analyze the following code features
        
        Code Features:
        {json.dumps(code_features, indent=2)[:8000]}

        Current date: {datetime.now().strftime('%Y-%m-%d')}
        """

        return system_message, user_prompt
    
    @staticmethod
    def file_selection(
        readme: Dict[str, Any],
        structure: Dict[str, Any],
        max_files: int = 25
    ) -> tuple[str, str]:
        system_message = f"""You are an expert software engineering analyst working for hackclub program Summer-of-making specializing in fraud detection and time-inflating.
        Your task is to select files that should be sent to a code analyzer from the repo to best represent the project while excluding templates, boilerplate, auto-generated content, and other non-essential files.

        You are also given the readme analysis of the project which includes an AI summary of the readme and a guess on how complex the project is. Using this data, try to select files that will be valuable for the code analyzer to detect fraud and time-inflating.

        Note: The files should be only be the code no config files, images, documentation, or other binary files.

        ONLY SELECT A MAXIMUM OF {max_files} FILES. If you think less files are needed, you can select less.
        """

        user_prompt = f"""
        AI Summary of README: {readme.get('summary', 'N/A')}
        
        Structure:
        {structure}

        Current date: {datetime.now().strftime('%Y-%m-%d')}
        Provide analysis in JSON format:
        {{
            "selected_files": [ "file_path1", "file_path2", ...]
        }}
        """

        return system_message, user_prompt
