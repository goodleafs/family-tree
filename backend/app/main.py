from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import init_db
from app.routers import auth_router, family_router, person_router
from app.routers.admin import router as admin_router
from app.routers.memorial import router as memorial_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时的清理工作

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于FastAPI+Vue3的多家族寻根家谱管理系统",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（上传的图片）
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(family_router, prefix="/api/v1")
app.include_router(person_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(memorial_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "寻根家谱管理系统API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
