# SlopScan Backend

A backend service for detecting AI-generated "slop" projects on GitHub using intelligent file analysis and selective downloading.

## Features

- GitHub repository structure analysis and mapping
- AI-powered selective file downloading using **Groq** (excludes templates, auto-generated content)
- RESTful API with FastAPI
- Smart file filtering based on content patterns and AI analysis
- **No GitHub token required** - works with public repositories using fallback methods

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Groq API key (GitHub token is optional)
```

3. Start the development server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /analyze` - Analyze a GitHub repository and get selective file downloads
- `GET /repo/{owner}/{repo}/structure` - Get repository structure
- `POST /repo/{owner}/{repo}/download` - Download selected files
- `GET /health` - Health check endpoint

## Architecture

- **API Layer**: FastAPI for REST endpoints
- **Analysis Engine**: AI-powered file classification using Groq
- **GitHub Integration**: Repository structure analysis with fallback support
- **File Filtering**: Smart exclusion of templates, auto-generated content, and boilerplate

## GitHub Access Methods

1. **With GitHub Token** (recommended): Higher rate limits, access to private repos
2. **Without Token**: Public repository access using GitHub API + web scraping fallback
3. **Web Scraping Fallback**: Used when API limits are exceeded or authentication fails
