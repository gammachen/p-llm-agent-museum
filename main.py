from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Museum Service API", version="1.0")

# 挂载静态文件目录
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

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
            "internal_management": "/api/internal/",
            "chat_interface": "/chat"
        }
    }

# Chat interface endpoint
@app.get("/chat")
def chat_interface():
    return FileResponse("chat_interface.html")

# Import and include routers
from services.core_orchestrator import router as core_router, SIMPLE_PATH_REDIRECTS
from services.public_services import router as public_router
from services.internal_services import router as internal_router

# 添加简单路径重定向
for path, target_path in SIMPLE_PATH_REDIRECTS.items():
    # 使用闭包函数正确捕获每个路径的target_path
    def create_redirect(endpoint_path):
        @app.get(path)
        async def redirect_to_api():
            return RedirectResponse(url=endpoint_path)
        return redirect_to_api
    
    create_redirect(target_path)

# Register routers
app.include_router(core_router)
app.include_router(public_router)
app.include_router(internal_router)