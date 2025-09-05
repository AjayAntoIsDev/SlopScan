"""
API routes for SlopScan backend
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import re

from app.models import (
    RepoRequest, AnalysisRequest, AnalysisResponse, 
    DownloadRequest, DownloadResponse, RepoStructure,
    CommitsResponse, CommitsCountResponse
)
from app.services.github import GitHubService
from app.services.ai import AIService
from app.services.summer_of_making import get_summer_service, SummerOfMakingService

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


@router.get("/repo/{owner}/{repo}/structure", response_model=RepoStructure)
async def get_repository_structure(
    owner: str,
    repo: str,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service)
):
    """Get the complete structure of a GitHub repository"""
    try:
        print(f"Getting repository structure for {owner}/{repo} on branch {branch}")
        print(f"Getting repository structure for owner={owner}, repo={repo}, branch={branch}")
        
        structure = await github_service.get_repo_structure(owner, repo, branch)
        return RepoStructure(**structure)
        
    except Exception as e:
        print(f"Failed to get repository structure for owner={owner}, repo={repo}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalysisRequest,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze a GitHub repository and use AI to selectively identify important files,
    excluding templates, auto-generated content, and boilerplate
    """
    try:
        print(f"Starting repository analysis for {request.owner}/{request.repo}")
        
        # Get repository structure
        structure = await github_service.get_repo_structure(request.owner, request.repo, request.branch)
        
        print(structure)
        # Use AI to analyze and select files
        ai_analysis = await ai_service.analyze_files_for_selection(
            structure["files"], 
            structure["analysis_summary"]
        )
        
        response = AnalysisResponse(
            owner=request.owner,
            repo=request.repo,
            branch=request.branch,
            selected_files=ai_analysis["selected_files"],
            excluded_files=ai_analysis["excluded_files"],
            analysis_summary=ai_analysis["analysis_summary"],
            total_selected=ai_analysis["total_selected"],
            total_excluded=ai_analysis["total_excluded"]
        )
        
        print(f"Repository analysis completed for {request.owner}/{request.repo}: selected={response.total_selected}, excluded={response.total_excluded}")
        
        return response
        
    except Exception as e:
        print(f"Analysis failed for {request.owner}/{request.repo}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repo/{owner}/{repo}/download", response_model=DownloadResponse)
async def download_files(
    owner: str,
    repo: str,
    request: DownloadRequest,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service)
):
    try:
        print(f"Starting file downloads for {owner}/{repo}: {len(request.file_paths)} files")
        
        downloaded_files = []
        total_size = 0
        
        for file_path in request.file_paths:
            if request.include_content:
                content = await github_service.download_file_content(owner, repo, file_path, branch)
                if content:
                    file_info = {
                        "path": file_path,
                        "name": file_path.split("/")[-1],
                        "size": len(content.encode('utf-8')),
                        "content": content
                    }
                    downloaded_files.append(file_info)
                    total_size += file_info["size"]
        
        response = DownloadResponse(
            files=downloaded_files,
            total_files=len(downloaded_files),
            total_size=total_size
        )
        
        print(f"File downloads completed for {owner}/{repo}: downloaded={len(downloaded_files)}, total_size={total_size}")
        
        return response
        
    except Exception as e:
        print(f"Download failed for {owner}/{repo}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repo/{owner}/{repo}/file/{file_path:path}/features")
async def extract_file_code_features(
    owner: str,
    repo: str,
    file_path: str,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service)
):
    try:
        print(f"Extracting code features for {owner}/{repo}/{file_path}")
        
        features = await github_service.extract_code_features(owner, repo, file_path, branch)
        
        if not features:
            raise HTTPException(status_code=404, detail="File not found or not supported")
        
        return features
        
    except Exception as e:
        print(f"File feature extraction failed for {file_path}: {e}")
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
            "repo_link": project_data.get("repo_link", None)
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
            "analyze": "POST /analyze - Analyze repository with AI",
            "structure": "GET /repo/{owner}/{repo}/structure - Get repository structure",
            "commits": "GET /repo/{owner}/{repo}/commits - Get repository commits with file changes",
            "commit_analysis": "GET /repo/{owner}/{repo}/commit-analysis - AI-powered commit analysis for fraud detection",
            "commits_count": "GET /repo/{owner}/{repo}/commits/count - Get total commits count efficiently",
            "download": "POST /repo/{owner}/{repo}/download - Download selected files",
            "code_features": "GET /repo/{owner}/{repo}/code-features - Extract code features using Tree-sitter",
            "file_features": "GET /repo/{owner}/{repo}/file/{file_path}/features - Extract features from specific file",
            "similarity_features": "GET /repo/{owner}/{repo}/similarity-features - Get features for code similarity analysis",
            "summer_project": "GET /som-analysis/project?project={id_or_url} - Get Summer of Making project data and devlogs"
        },
        "supported_languages": [
            "python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "ruby", "php"
        ]
    }