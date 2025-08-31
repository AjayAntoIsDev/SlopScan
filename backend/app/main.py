"""
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.api.routes import router as api_router



app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.api_title,
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print("Starting SlopScan backend")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("Shutting down SlopScan backend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
