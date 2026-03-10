import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
from app.config import settings

# 确保上传目录存在
UPLOAD_PATH = Path(settings.UPLOAD_DIR)
try:
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    print(f"上传目录: {UPLOAD_PATH}")
except Exception as e:
    print(f"创建上传目录失败: {e}")
    # 如果创建失败，使用当前目录
    UPLOAD_PATH = Path("uploads")
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

# 缩略图尺寸
THUMBNAIL_SIZE = (200, 200)

def validate_image(file: UploadFile) -> None:
    """验证上传的图片文件"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。允许的类型: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )

def save_upload_file(file: UploadFile, subfolder: str = "photos") -> str:
    """保存上传的文件"""
    try:
        validate_image(file)
        
        # 创建子目录
        sub_path = UPLOAD_PATH / subfolder
        sub_path.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = sub_path / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 生成缩略图
        try:
            create_thumbnail(file_path, sub_path / f"thumb_{unique_filename}")
        except Exception as e:
            print(f"缩略图生成失败: {e}")
            pass  # 缩略图生成失败不影响主文件
        
        # 返回相对路径
        return f"/uploads/{subfolder}/{unique_filename}"
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"文件上传失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        # 安全关闭文件
        try:
            if hasattr(file, 'file') and file.file and not file.file.closed:
                file.file.close()
        except Exception:
            pass

def create_thumbnail(image_path: Path, thumb_path: Path) -> None:
    """创建缩略图"""
    with Image.open(image_path) as img:
        # 转换为RGB（处理PNG透明背景）
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # 生成缩略图
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)

def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        full_path = UPLOAD_PATH.parent / file_path.lstrip('/')
        if full_path.exists():
            full_path.unlink()
            # 尝试删除对应的缩略图
            thumb_path = full_path.parent / f"thumb_{full_path.name}"
            if thumb_path.exists():
                thumb_path.unlink()
            return True
    except Exception:
        pass
    return False
