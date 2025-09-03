"""
API routes for SlopScan backend
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import re

from app.models import (
    RepoRequest, AnalysisRequest, AnalysisResponse, 
    DownloadRequest, DownloadResponse, RepoStructure
)
from app.services.github import GitHubService
from app.services.ai import AIService

router = APIRouter()

# Dependency injection
def get_github_service() -> GitHubService:
    return GitHubService()

def get_ai_service() -> AIService:
    return AIService()

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


@router.get("/repo-analysis")
async def repo_analysis(url: str):
    """Repository analysis endpoint that takes a repository URL"""
    # TODO: Implement repository analysis logic
    return {
        "url": url,
        "message": "Repository analysis endpoint - implementation pending"
    }


@router.get("/repo-analysis/readme-analysis")
async def readme_analysis(
    repo_url: str,
    github_service: GitHubService = Depends(get_github_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """README analysis endpoint that fetches and analyzes README content using AI"""
    try:
        owner, repo = parse_github_url(repo_url)
        
        readme_content = await github_service.get_readme_content(owner, repo)
        
        if not readme_content:
            raise HTTPException(status_code=404, detail="README not found in repository")
        
        analysis = await ai_service.analyze_readme(readme_content, repo_url)
        
        return {
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "content_length": len(readme_content),
            "probability": analysis.get("probability", None),
            "reasoning": analysis.get("reasoning", None)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to analyze README: {str(e)}")


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SlopScan API",
        "description": "AI-powered GitHub repository analysis and selective file downloading with Tree-sitter code extraction",
        "endpoints": {
            "analyze": "POST /analyze - Analyze repository with AI",
            "structure": "GET /repo/{owner}/{repo}/structure - Get repository structure",
            "download": "POST /repo/{owner}/{repo}/download - Download selected files",
            "code_features": "GET /repo/{owner}/{repo}/code-features - Extract code features using Tree-sitter",
            "file_features": "GET /repo/{owner}/{repo}/file/{file_path}/features - Extract features from specific file",
            "similarity_features": "GET /repo/{owner}/{repo}/similarity-features - Get features for code similarity analysis"
        },
        "supported_languages": [
            "python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "ruby", "php"
        ]
    }