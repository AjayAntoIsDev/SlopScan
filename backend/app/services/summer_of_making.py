import httpx
from typing import Dict, Optional, Any
from app.config import settings


class SummerOfMakingService:
    BASE_URL = "https://summer.hackclub.com/api"
    
    def __init__(self, session_cookie: Optional[str] = None):
        cookie = session_cookie or settings.summer_session_cookie
        
        if not cookie:
            raise Exception("Summer of Making session cookie is required. Please set SUMMER_SESSION_COOKIE in your .env file.")
        
        headers = {
            'Cookie': cookie,
        }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=headers,
            follow_redirects=True
        )
    
    async def close(self):
        await self.client.aclose()
    
    async def get_project_data(self, project_id: int) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.BASE_URL}/v2/projects/{project_id}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                try:
                    # Fallback to v1 API with devlogs parameter
                    url = f"{self.BASE_URL}/v1/projects/{project_id}?devlogs=true"
                    response = await self.client.get(url)
                    response.raise_for_status()
                    return response.json()
                except Exception:
                    return None
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Error fetching project data: {str(e)}")


# Singleton instance
_summer_service: Optional[SummerOfMakingService] = None

async def get_summer_service() -> SummerOfMakingService:
    global _summer_service
    if _summer_service is None:
        _summer_service = SummerOfMakingService()
    return _summer_service

async def cleanup_summer_service():
    global _summer_service
    if _summer_service:
        await _summer_service.close()
        _summer_service = None
