"""
API routes for SlopScan backend
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import structlog

from app.models import (
    RepoRequest, AnalysisRequest, AnalysisResponse, 
    DownloadRequest, DownloadResponse, RepoStructure
)
from app.services.github import GitHubService
from app.services.ai import AIService

logger = structlog.get_logger()
router = APIRouter()

# Dependency injection
def get_github_service() -> GitHubService:
    return GitHubService()

def get_ai_service() -> AIService:
    return AIService()


@router.get("/repo/{owner}/{repo}/structure", response_model=RepoStructure)
async def get_repository_structure(
    owner: str,
    repo: str,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service)
):
    """Get the complete structure of a GitHub repository"""
    try:
        logger.info("Getting repository structure", owner=owner, repo=repo, branch=branch)
        
        structure = await github_service.get_repo_structure(owner, repo, branch)
        return RepoStructure(**structure)
        
    except Exception as e:
        logger.error("Failed to get repository structure", error=str(e), owner=owner, repo=repo)
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
        logger.info("Starting repository analysis", owner=request.owner, repo=request.repo)
        
        # Get repository structure
        structure = await github_service.get_repo_structure(request.owner, request.repo, request.branch)
        
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
        
        logger.info(
            "Repository analysis completed",
            owner=request.owner,
            repo=request.repo,
            selected=response.total_selected,
            excluded=response.total_excluded
        )
        
        return response
        
    except Exception as e:
        logger.error("Analysis failed", error=str(e), owner=request.owner, repo=request.repo)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repo/{owner}/{repo}/download", response_model=DownloadResponse)
async def download_files(
    owner: str,
    repo: str,
    request: DownloadRequest,
    branch: str = "main",
    github_service: GitHubService = Depends(get_github_service)
):
    """Download the content of specific files from a repository"""
    try:
        logger.info("Starting file downloads", owner=owner, repo=repo, file_count=len(request.file_paths))
        
        downloaded_files = []
        total_size = 0
        
        for file_path in request.file_paths:
            if request.include_content:
                content = await github_service.download_file_content(owner, repo, file_path, branch)
                if content:
                    # Create file info with content
                    file_info = {
                        "path": file_path,
                        "name": file_path.split("/")[-1],
                        "size": len(content.encode('utf-8')),
                        "type": "file",
                        "content": content
                    }
                    downloaded_files.append(file_info)
                    total_size += file_info["size"]
        
        response = DownloadResponse(
            files=downloaded_files,
            total_files=len(downloaded_files),
            total_size=total_size
        )
        
        logger.info(
            "File downloads completed",
            owner=owner,
            repo=repo,
            downloaded=len(downloaded_files),
            total_size=total_size
        )
        
        return response
        
    except Exception as e:
        logger.error("Download failed", error=str(e), owner=owner, repo=repo)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SlopScan API",
        "description": "AI-powered GitHub repository analysis and selective file downloading",
        "endpoints": {
            "analyze": "POST /analyze - Analyze repository with AI",
            "structure": "GET /repo/{owner}/{repo}/structure - Get repository structure",
            "download": "POST /repo/{owner}/{repo}/download - Download selected files"
        }
    }
