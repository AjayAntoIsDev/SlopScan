# API Usage Examples

Here are some examples of how to use the SlopScan API with Groq AI and optional GitHub authentication:

## Quick Start (No GitHub Token Required)

You can analyze public repositories without any GitHub token! Just need a Groq API key.

```bash
# Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# Start the server
./start.sh
```

## 1. Analyze a Repository

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "repo_url": "https://github.com/fastapi/fastapi",
       "owner": "fastapi",
       "repo": "fastapi",
       "branch": "main",
       "max_files": 100
     }'
```

## 2. Get Repository Structure

```bash
curl -X GET "http://localhost:8000/api/v1/repo/fastapi/fastapi/structure?branch=main"
```

## 3. Download Selected Files

```bash
curl -X POST "http://localhost:8000/api/v1/repo/fastapi/fastapi/download?branch=main" \
     -H "Content-Type: application/json" \
     -d '{
       "file_paths": [
         "fastapi/main.py",
         "README.md",
         "pyproject.toml"
       ],
       "include_content": true
     }'
```

## Example Response Structure

### Analysis Response
```json
{
  "owner": "fastapi",
  "repo": "fastapi",
  "branch": "main",
  "selected_files": [
    {
      "path": "fastapi/main.py",
      "name": "main.py",
      "size": 1250,
      "type": "file",
      "ai_confidence": 0.95,
      "reason": "Core application entry point"
    }
  ],
  "excluded_files": [
    {
      "path": "tests/test_example.py",
      "name": "test_example.py", 
      "size": 800,
      "type": "file",
      "reason": "Test file - excluded from core implementation"
    }
  ],
  "analysis_summary": {
    "primary_language": "Python",
    "project_type": "web framework",
    "architecture_pattern": "MVC",
    "key_insights": ["Modern async web framework", "Well-structured codebase"]
  },
  "total_selected": 25,
  "total_excluded": 150
}
```

## Python Usage

```python
import requests

# Analyze repository
response = requests.post("http://localhost:8000/api/v1/analyze", json={
    "repo_url": "https://github.com/fastapi/fastapi",
    "owner": "fastapi", 
    "repo": "fastapi",
    "branch": "main"
})

analysis = response.json()
print(f"Selected {analysis['total_selected']} files")
print(f"Excluded {analysis['total_excluded']} files")

# Download important files
important_files = [f['path'] for f in analysis['selected_files'][:10]]
download_response = requests.post(
    "http://localhost:8000/api/v1/repo/fastapi/fastapi/download",
    json={"file_paths": important_files, "include_content": True}
)

downloads = download_response.json()
for file_info in downloads['files']:
    print(f"Downloaded: {file_info['path']} ({file_info['size']} bytes)")
```
