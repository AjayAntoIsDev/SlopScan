#!/usr/bin/env python3
"""
Quick test script for SlopScan backend with Groq
"""
import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_slopscan():
    """Test the SlopScan API"""
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("🏥 Testing health endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/health") as response:
            if response.status == 200:
                health = await response.json()
                print(f"✅ Health check passed: {health['status']}")
            else:
                print(f"❌ Health check failed: {response.status}")
                return
    
    # Test repository analysis
    print("\n🔍 Testing repository analysis...")
    owner = "octocat"  # GitHub's mascot account with simple repos
    repo = "Hello-World"  # Simple test repository
    
    payload = {
        "repo_url": f"https://github.com/{owner}/{repo}",
        "owner": owner,
        "repo": repo,
        "branch": "master",  # Hello-World uses master branch
        "max_files": 50
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{base_url}/api/v1/analyze", json=payload) as response:
                if response.status == 200:
                    analysis = await response.json()
                    print(f"✅ Analysis successful!")
                    print(f"   📁 Repository: {analysis['owner']}/{analysis['repo']}")
                    print(f"   ✨ Selected files: {analysis['total_selected']}")
                    print(f"   🚫 Excluded files: {analysis['total_excluded']}")
                    
                    if analysis['selected_files']:
                        print(f"\n📄 First few selected files:")
                        for file_info in analysis['selected_files'][:3]:
                            reason = file_info.get('reason', 'No reason provided')
                            confidence = file_info.get('ai_confidence', 0)
                            print(f"   • {file_info['path']} (confidence: {confidence:.2f}) - {reason}")
                    
                    return analysis
                else:
                    error = await response.text()
                    print(f"❌ Analysis failed: {response.status} - {error}")
                    return None
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("   Make sure the server is running: uvicorn app.main:app --reload")
            return None

async def main():
    print("🚀 SlopScan Backend Test")
    print("=" * 40)
    
    # Check environment
    groq_key = os.getenv("GROQ_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    print(f"🔑 Groq API Key: {'✅ Set' if groq_key else '❌ Missing'}")
    print(f"🐙 GitHub Token: {'✅ Set (better rate limits)' if github_token else '⚠️  Not set (using public API)'}")
    
    if not groq_key:
        print("\n❌ GROQ_API_KEY is required!")
        print("   Get your free API key at: https://console.groq.com/")
        return
    
    await test_slopscan()

if __name__ == "__main__":
    asyncio.run(main())
