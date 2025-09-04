"""
Pydantic models for API requests and responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl


class RepoRequest(BaseModel):
    """Request model for repository analysis"""
    repo_url: HttpUrl
    owner: str
    repo: str
    branch: Optional[str] = "main"


class FileInfo(BaseModel):
    """Information about a file in the repository"""
    path: str
    name: str
    size: int
    download_url: Optional[str] = None
    ignore: bool = False


class RepoStructure(BaseModel):
    """Repository structure response"""
    owner: str
    repo: str
    branch: str
    total_files: int
    total_size: int
    files: List[FileInfo]
    summary: Dict[str, Any]


class AnalysisRequest(BaseModel):
    """Request model for AI analysis"""
    repo_url: HttpUrl
    owner: str
    repo: str
    branch: Optional[str] = "main"
    max_files: Optional[int] = 100
    exclude_patterns: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    """Response model for AI analysis"""
    owner: str
    repo: str
    branch: str
    selected_files: List[FileInfo]
    excluded_files: List[FileInfo]
    analysis_summary: Dict[str, Any]
    total_selected: int
    total_excluded: int


class DownloadRequest(BaseModel):
    """Request model for file downloads"""
    file_paths: List[str]
    include_content: bool = True


class DownloadedFile(BaseModel):
    """Information about a downloaded file"""
    path: str
    name: str
    size: int
    content: str

class DownloadResponse(BaseModel):
    """Response model for file downloads"""
    files: List[DownloadedFile]
    total_files: int
    total_size: int


class FileChange(BaseModel):
    """Information about a file change in a commit"""
    filename: str
    status: str  # "added", "modified", "removed"
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


class CommitInfo(BaseModel):
    """Information about a repository commit"""
    sha: str
    message: str
    author_name: str
    author_email: str
    date: str
    files_changed: List[FileChange]
    total_additions: int
    total_deletions: int
    total_files: int


class CommitsResponse(BaseModel):
    """Response model for repository commits"""
    owner: str
    repo: str
    branch: str
    commits: List[CommitInfo]
    total_commits: int


class CommitsCountResponse(BaseModel):
    """Response model for total commits count"""
    repo_url: str
    owner: str
    repo: str
    branch: str
    total_commits: int
    method: str  # "pagination_headers" or "fallback"
