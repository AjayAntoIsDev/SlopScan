"""
Configuration module for SlopScan backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    debug: bool = False
    env: str = "production"
    
    # GitHub API (optional - will use public GitHub API if not provided)
    github_token: str = ""
    github_api_url: str = "https://api.github.com"
    
    # AI Services - Groq
    groq_api_key: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "SlopScan API"
    api_version: str = "1.0.0"
    
    # Security
    secret_key: str = "your_secret_key_here"
    
    # Logging
    log_level: str = "INFO"
    
    # File Processing
    max_file_size_mb: int = 10
    max_files_per_repo: int = 1000
    allowed_extensions: str = ".py,.js,.ts,.java,.cpp,.c,.go,.rs,.rb,.php,.cs,.swift,.kt,.scala,.r,.sql,.md,.txt,.yml,.yaml,.json,.xml,.html,.css,.scss,.less,.vue,.jsx,.tsx,.toml,.ini,.cfg,.conf"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
