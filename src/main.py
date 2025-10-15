from src.config import settings

if __name__ == "__main__":
    import uvicorn
    
    # Hot-reload is enabled by default, disabled only in production
    hot_reload = not settings.is_production
    
    print(f"Starting API server:")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Hot-reload: {hot_reload}")
    
    uvicorn.run(
        "src.api.server:app", 
        host="0.0.0.0", 
        port=settings.API_PORT, 
        reload=hot_reload
    )
