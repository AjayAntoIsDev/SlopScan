"""
Example usage and testing script for SlopScan backend
"""
import asyncio
import json
import aiohttp
from typing import Dict, Any


class SlopScanClient:
    """Client for testing SlopScan API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def analyze_repository(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Any]:
        """Analyze a GitHub repository"""
        url = f"{self.base_url}/api/v1/analyze"
        payload = {
            "repo_url": f"https://github.com/{owner}/{repo}",
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "max_files": 100
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
    
    async def get_structure(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Any]:
        """Get repository structure"""
        url = f"{self.base_url}/api/v1/repo/{owner}/{repo}/structure"
        params = {"branch": branch}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
    
    async def download_files(self, owner: str, repo: str, file_paths: list, branch: str = "main") -> Dict[str, Any]:
        """Download specific files"""
        url = f"{self.base_url}/api/v1/repo/{owner}/{repo}/download"
        payload = {
            "file_paths": file_paths,
            "include_content": True
        }
        params = {"branch": branch}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")


async def example_usage():
    """Example usage of the SlopScan API"""
    client = SlopScanClient()
    
    # Example repository to analyze
    owner = "fastapi"
    repo = "fastapi"
    
    print(f"🔍 Analyzing repository: {owner}/{repo}")
    
    try:
        # Step 1: Get repository structure
        print("\n📁 Getting repository structure...")
        structure = await client.get_structure(owner, repo)
        print(f"   Total files: {structure['total_files']}")
        print(f"   Total size: {structure['total_size']} bytes")
        print(f"   Languages: {list(structure['analysis_summary']['languages'].keys())}")
        
        # Step 2: AI-powered analysis and selection
        print("\n🤖 Running AI analysis...")
        analysis = await client.analyze_repository(owner, repo)
        print(f"   Selected files: {analysis['total_selected']}")
        print(f"   Excluded files: {analysis['total_excluded']}")
        
        # Print some selected files
        print("\n✅ Selected files (first 10):")
        for file_info in analysis['selected_files'][:10]:
            confidence = file_info.get('ai_confidence', 0)
            reason = file_info.get('reason', 'No reason provided')
            print(f"   📄 {file_info['path']} (confidence: {confidence:.2f}) - {reason}")
        
        # Print some excluded files
        print("\n❌ Excluded files (first 10):")
        for file_info in analysis['excluded_files'][:10]:
            reason = file_info.get('reason', 'No reason provided')
            print(f"   🚫 {file_info['path']} - {reason}")
        
        # Step 3: Download a few important files
        important_files = [f['path'] for f in analysis['selected_files'][:5]]
        if important_files:
            print(f"\n📥 Downloading {len(important_files)} important files...")
            downloads = await client.download_files(owner, repo, important_files)
            
            for file_info in downloads['files']:
                content_preview = file_info['content'][:200] + "..." if len(file_info['content']) > 200 else file_info['content']
                print(f"\n📄 {file_info['path']} ({file_info['size']} bytes):")
                print(f"   {content_preview}")
        
        print(f"\n🎉 Analysis complete! Summary:")
        print(f"   📊 {analysis['analysis_summary']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 SlopScan API Example Usage")
    print("=" * 50)
    asyncio.run(example_usage())
