from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os

app = FastAPI(title="Museum Service API", version="1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Museum Service API",
        "endpoints": {
            "public_services": "/api/public/",
            "internal_management": "/api/internal/"
        }
    }

# Import and include routers
from services.core_orchestrator import router as core_router, SIMPLE_PATH_REDIRECTS
from services.public_services import router as public_router
from services.internal_services import router as internal_router

# 添加简单路径重定向
for path, target_path in SIMPLE_PATH_REDIRECTS.items():
    @app.get(path)
    async def redirect_to_api():
        return RedirectResponse(url=target_path)

# Register routers
app.include_router(core_router)
app.include_router(public_router)
app.include_router(internal_router)