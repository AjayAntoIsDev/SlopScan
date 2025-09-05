"""
API routes for SlopScan backend
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import re

from app.models import (
    RepoRequest, AnalysisRequest, AnalysisResponse, 
    DownloadRequest, DownloadResponse, RepoStructure,
    CommitsResponse, CommitsCountResponse
)
from app.services.github import GitHubService
from app.services.ai import AIService
from app.services.summer_of_making import get_summer_service, SummerOfMakingService
from app.services.prompts import PromptTemplates

router = APIRouter()

# Dependency injection
def get_github_service() -> GitHubService:
    return GitHubService()

def get_ai_service() -> AIService:
    return AIService()

async def get_summer_of_making_service() -> SummerOfMakingService:
    return await get_summer_service()

def parse_github_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub URL to extract owner and repo name
    
    Args:
        repo_url: GitHub repository URL or owner/repo format
        
    Returns:
        Tuple of (owner, repo)
        
    Raises:
        ValueError: If URL format is invalid
    """
    github_pattern = r"(?:github\.com/)?([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$"
    match = re.search(github_pattern, repo_url)
    
    if not match:
        raise ValueError("Invalid GitHub repository URL")
    
    return match.groups()

def parse_summer_project_url(project_input: str) -> int:
    """
    Parse Summer of Making project URL or ID to extract project ID
    
    Args:
        project_input: Summer of Making project URL or project ID
        
    Returns:
        Project ID as integer
        
    Raises:
        ValueError: If format is invalid
    """
    # If it's already a number, return it
    if project_input.isdigit():
        return int(project_input)
    
    # Try to extract project ID from URL
    summer_pattern = r"(?:summer\.hackclub\.com/projects/)?(\d+)/?(?:\?.*)?$"
    match = re.search(summer_pattern, project_input)
    
    if match:
        return int(match.group(1))
    
    raise ValueError("Invalid Summer of Making project URL or ID")


@router.get("/code-analysis")
async def analyze_code_features(
    repo_url: str = None,
    features: List[Dict[str, Any]] = None,
    branch: str = "main",
    max_files: int = 20,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        if features is not None:
            print(f"Analyzing provided code features: {len(features)} files")
            code_features = features
            analysis_source = "provided_features"
            repo_info = {"source": "external_features"}
        
        elif repo_url is not None:
            print(f"Extracting code features using get_code_features for {repo_url}")
            
            features_response = await get_code_features(
                repo_url=repo_url,
                branch=branch,
                max_files=max_files,
                file_paths=None,
                github_service=github_service,
                ai_service=ai_service
            )
            
            code_features = features_response.get("files", [])
            repo_info = {
                "owner": features_response.get("owner"),
                "repo": features_response.get("repo"),
                "branch": features_response.get("branch"),
                "repo_url": features_response.get("repo_url"),
                "total_files_analyzed": len(code_features)
            }
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either repo_url or features must be provided"
            )
        
        if not code_features:
            raise HTTPException(
                status_code=404,
                detail="No code features found to analyze"
            )
        
        print(f"Running AI analysis on {len(code_features)} files")
        ai_analysis = await ai_service.analyze_code(code_features)
        
        response = {
            "repo_info": repo_info,
            "total_files_analyzed": len(code_features),
            "code_features": code_features,
            "ai_analysis": ai_analysis,
        }
        
        print(f"Code analysis completed: analyzed {len(code_features)} files")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to analyze code features: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/code-analysis/code-features")
async def get_code_features(
    repo_url: str,
    branch: str = "main",
    max_files: int = 20,
    file_paths: List[str] = None,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        max_files = 20
        owner, repo = parse_github_url(repo_url)
        print(f"Starting code feature extraction analysis for {owner}/{repo} on branch {branch}")
        
        if file_paths is not None:
            print(f"Using provided file paths for analysis: {len(file_paths)} files")
            selected_files = file_paths
        else:
            readme_content = await github_service.get_readme_content(owner, repo, branch)
            if readme_content:
                readme_analysis = await ai_service.analyze_readme(readme_content, repo_url)

            structure = await github_service.get_repo_structure(owner, repo, branch)
            
            print("Running AI file selection for feature extraction")
            file_selection = await ai_service.select_files_for_analysis(
                readme_analysis=readme_analysis or {},
                structure=structure,
            )
            
            selected_files = file_selection.get("selected_files", [])
        
        if len(selected_files) > max_files:
            print(f"Limiting analysis to {max_files} files (selected {len(selected_files)})")
            selected_files = selected_files[:max_files]
        
        files = []
        total_features = {
            "total_functions": 0,
            "total_classes": 0,
            "total_variables": 0,
            "total_comments": 0,
            "programming_languages": set(),
        }
        
        for file_path in selected_files:
            try:
                print(f"Extracting features from {file_path}")
                
                file_content = await github_service.download_file_content(owner, repo, file_path, branch)
                if not file_content:
                    continue
                
                features = await github_service.extract_code_features(owner, repo, file_path, branch)
                
                if features:
                    file_extension = file_path.split('.')[-1] if '.' in file_path else 'unknown'
                    
                    file_analysis = {
                        "name": file_path.split("/")[-1],
                        "language": features.get("language", "unknown"),
                        "features": features,
                    }
                    
                    files.append(file_analysis)
                    
                    if features.get("language"):
                        total_features["programming_languages"].add(features["language"])
                    
                    total_features["total_functions"] += len(
                        features.get("function_names", []))
                    total_features["total_classes"] += len(features.get("classes_names", []))
                    total_features["total_variables"] += len(features.get("variables_names", []))
                    total_features["total_comments"] += len(features.get("comments", []))
                    
                
            except Exception as e:
                print(f"Failed to extract features from {file_path}: {e}")
                continue
        
        total_features["programming_languages"] = list(total_features["programming_languages"])
        
        response = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "repo_url": f"https://github.com/{owner}/{repo}",
            "analysis_summary": {
                "total_files_in_repo": structure.get("total_files", 0),
                "files_selected_for_analysis": len(file_selection.get("selected_files", [])),
                "files_analyzed_in_detail": len(files),
                "readme_available": readme_analysis is not None
            },
            "readme_analysis": readme_analysis,
            "file_selection": file_selection,
            "files": files,
            "aggregated_features": total_features,
        }
        
        print(
            f"Detailed code analysis completed for {owner}/{repo}: analyzed {len(files)} files")
        
        return response
        
    except Exception as e:
        print(f"Failed to perform detailed code analysis for {repo_url}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/code-analysis/structure")
async def get_repository_structure(
    repo_url: str,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        owner, repo = parse_github_url(repo_url)
        print(f"Getting repository structure for {owner}/{repo}")
        
        structure = await github_service.get_repo_structure(owner, repo)
        
        readme_content = await github_service.get_readme_content(owner, repo)
        
        readme_analysis = None
        if readme_content:
            repo_url = f"https://github.com/{owner}/{repo}"
            readme_analysis = await ai_service.analyze_readme(readme_content, repo_url)

        
        print("Running AI file selection for analysis")
        file_selection = await ai_service.select_files_for_analysis(
            readme_analysis=readme_analysis,
            structure=structure
        )
        
        print(f"Repository structure analysis completed for {owner}/{repo}")
        
        return file_selection
        
    except Exception as e:
        print(f"Failed to get repository structure for {owner}/{repo}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repo-analysis/readme-analysis")
async def readme_analysis(
    repo_url: str,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        owner, repo = parse_github_url(repo_url)
        
        readme_content = await github_service.get_readme_content(owner, repo, branch)
        
        if not readme_content:
            raise HTTPException(status_code=404, detail="README not found in repository")
        
        analysis = await ai_service.analyze_readme(readme_content, repo_url)
        
        return {
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "content_length": len(readme_content),
            "probability": analysis.get("probability", None),
            "reasoning": analysis.get("reasoning", None),
            "summary": analysis.get("summary", None),
            "complexity": analysis.get("complexity", None)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze README: {str(e)}")


@router.get("/repo-analysis/commits")
async def commits(
    repo_url: str,
    branch: str = "main",
    per_page: int = 100,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        owner, repo = parse_github_url(repo_url)
        
        total_commits = await github_service.get_total_commits_count(owner, repo, branch)
        
        commits_data = await github_service.get_repository_commits(owner, repo, branch, per_page)
        
        ai_commits_analysis = await ai_service.analyze_commits(commits_data, {"owner": owner, "repo": repo, "branch": branch}
                                                               )
        if not commits_data or not commits_data.get("commits"):
            raise HTTPException(status_code=404, detail="No commits found in repository")
        
        
        return {
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "total_commits": total_commits, 
            "commits_got": len(commits_data.get("commits", [])),
            "commits": commits_data.get("commits", []),
            "analysis": ai_commits_analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze commits: {str(e)}")


@router.get("/repo-analysis/commits-count")
async def commits_count(
    repo_url: str,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service),
):
    try:
        owner, repo = parse_github_url(repo_url)

        total_commits = await github_service.get_total_commits_count(owner, repo, branch)

        return {
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "total_commits": total_commits
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to analyze commits: {str(e)}")
    

@router.get("/repo-analysis/commits-analysis")
async def analyze_repository_commits(
    repo_url: str,
    branch: str = "main",
    per_page: int = 100,
    include_readme_context: bool = True,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        owner, repo = parse_github_url(repo_url)

        print(f"Starting commit analysis for {owner}/{repo} on branch {branch}")
        
        total_commits = await github_service.get_total_commits_count(owner, repo, branch)
        
        commits_data = await github_service.get_repository_commits(owner, repo, branch, per_page)
        
        if not commits_data or not commits_data.get("commits"):
            raise HTTPException(status_code=404, detail="No commits found in repository")
        
        readme_analysis = None
        if include_readme_context:
            try:
                readme_content = await github_service.get_readme_content(owner, repo, branch)
                if readme_content:
                    readme_analysis = await ai_service.analyze_readme(readme_content, f"https://github.com/{owner}/{repo}")
            except Exception as e:
                print(f"Failed to get README context: {e}")
        
        repo_info = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "total_commits": total_commits
        }
        
        commit_analysis = await ai_service.analyze_commits(
            commits_data=commits_data.get("commits", []),
            repo_info=repo_info,
            readme_analysis=readme_analysis
        )
        
        response = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "total_commits": total_commits,
            "commits_analyzed": len(commits_data.get("commits", [])),
            "analysis": commit_analysis,
            "readme_context_included": readme_analysis is not None,
            "analysis_metadata": {
                "timestamp": "analyzed",
                "method": "ai_analysis",
                "sample_size": len(commits_data.get("commits", []))
            }
        }
        
        print(f"Commit analysis completed for {owner}/{repo}: analyzed {len(commits_data.get('commits', []))} commits")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Commit analysis failed for {owner}/{repo}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to analyze commits: {str(e)}")


@router.post("/repo-analysis/slop-score")
async def calculate_slop_score(
    readme_analysis: Dict[str, Any],
    repo_analysis: Dict[str, Any], 
    som_analysis: Dict[str, Any],
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        print("Calculating slop score from provided analyses")
        
        
        system_message, user_prompt = PromptTemplates.repo_slopscore(
            readme=readme_analysis,
            repo_analysis=repo_analysis,
            som_analysis=som_analysis
        )
        
        response = await ai_service.client.prompt(
            prompt=user_prompt,
            system_message=system_message,
            temperature=0.3,
            max_tokens=2000
        )
        
        slop_analysis = ai_service._parse_json_response(response)
        
        if "error" in slop_analysis:
            return {
                "error": slop_analysis["error"],
                "raw_response": slop_analysis.get("raw_analysis", response),
                "input_summaries": {
                    "readme_provided": readme_analysis is not None,
                    "repo_analysis_provided": repo_analysis is not None,
                    "som_analysis_provided": som_analysis is not None
                }
            }
        
        print(f"Slop score calculation completed: {slop_analysis.get('slopscore', 'N/A')}")
        
        return slop_analysis
        
    except Exception as e:
        print(f"Slop score calculation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to calculate slop score: {str(e)}")


@router.get("/som-analysis/project")
async def get_summer_project(
    project: str,
    summer_service: SummerOfMakingService = Depends(get_summer_of_making_service)
):
    try:
        project_id = parse_summer_project_url(project)
        
        print(f"Fetching Summer of Making project {project_id}")
        
        project_data = await summer_service.get_project_data(project_id)
        
        if not project_data:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        response = {
            "project_id": project_id,
            "title": project_data.get("title"),
            "description": project_data.get("description"),
            "created_at": project_data.get("created_at"),
            "updated_at": project_data.get("updated_at"),
            "devlogs_count": len(project_data.get("devlogs", [])),
            "devlogs": project_data.get("devlogs", []),
            "repo_link": project_data.get("repo_link", None),
            "total_time_coded": project_data.get("total_seconds_coded", None)
        }
        
        print(f"Successfully fetched Summer of Making project {project_id} with {response['devlogs_count']} devlogs")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to fetch Summer of Making project: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch project data: {str(e)}")

@router.get("/som-analysis")
async def get_summer_analysis(
    project: str,
    summer_service: SummerOfMakingService = Depends(get_summer_of_making_service),
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    try:
        project_id = parse_summer_project_url(project)
        
        print(f"Starting comprehensive analysis for Summer of Making project {project_id}")
        
        project_data = await summer_service.get_project_data(project_id)
        
        if not project_data:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        repo_analysis = None
        repo_url = project_data.get("repo_link")
        
        if repo_url:
            owner, repo = parse_github_url(repo_url)
            
            total_commits = await github_service.get_total_commits_count(owner, repo, "main")
            commits_data = await github_service.get_repository_commits(owner, repo, "main", 100)
            
            readme_analysis = None
            try:
                readme_content = await github_service.get_readme_content(owner, repo, "main")
                if readme_content:
                    readme_analysis = await ai_service.analyze_readme(readme_content, repo_url)
            except Exception as e:
                print(f"Failed to get README analysis: {e}")
            
            repo_analysis = {
                "owner": owner,
                "repo": repo,
                "total_commits": total_commits,
                "commits": commits_data.get("commits", []) if commits_data else [],
                "readme_analysis": readme_analysis
            }
        
        print(f"Running AI analysis for project {project_id}")
        ai_analysis = await ai_service.analyze_som(project_data, repo_analysis)
        
        response = {
            "project_id": project_id,
            "project_title": project_data.get("title"),
            "project_description": project_data.get("description"),
            "devlogs_count": len(project_data.get("devlogs", [])),
            "repo_link": repo_url,
            "ai_analysis": ai_analysis,
            "total_time_coded": project_data.get("total_seconds_coded", None),
            "readme_analysis": repo_analysis.get("readme_analysis") if repo_analysis else None,
        }
        
        print(f"Comprehensive analysis completed for Summer of Making project {project_id}")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to analyze Summer of Making project: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to analyze project: {str(e)}")

    
@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SlopScan API",
        "description": "AI-powered GitHub repository analysis and selective file downloading with Tree-sitter code extraction",
        "endpoints": {
            "code_analysis": "POST /code-analysis - Analyze code features (provide repo_url OR features list)",
            "code_features": "GET /code-analysis/code-features - Extract and return code features from repository",
            "structure_analysis": "GET /code-analysis/structure - Repository structure analysis and file selection",
            "readme_analysis": "GET /repo-analysis/readme-analysis - AI analysis of README content",
            "commits_analysis": "GET /repo-analysis/commits-analysis - AI-powered commit analysis for fraud detection",
            "commits": "GET /repo-analysis/commits - Get repository commits with AI analysis",
            "commits_count": "GET /repo-analysis/commits-count - Get total commits count efficiently",
            "slop_score": "POST /repo-analysis/slop-score - Calculate slop score from provided analyses",
            "summer_project": "GET /som-analysis/project?project={id_or_url} - Get Summer of Making project data and devlogs",
            "summer_analysis": "GET /som-analysis?project={id_or_url} - Comprehensive Summer of Making project analysis"
        },
        "supported_languages": [
            "python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "ruby", "php"
        ],
        "features": {
            "fraud_detection": "AI-powered analysis to detect fraudulent projects and time inflation",
            "code_analysis": "Tree-sitter powered code feature extraction (functions, classes, variables, comments)",
            "file_selection": "Smart file selection excluding templates and boilerplate",
            "summer_of_making": "Integration with Hack Club's Summer of Making program analysis"
        }
    }