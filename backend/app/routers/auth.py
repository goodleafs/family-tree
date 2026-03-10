from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate, Token, UserLogin
from app.services import AuthService
from app.utils import create_access_token, verify_token, save_upload_file, delete_file, _truncate_password
from app.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user_db = await AuthService.get_user_by_username(db, username)
    if user_db is None:
        raise credentials_exception
    if user_db.is_active is False:  # 修复SQLAlchemy布尔比较语法错误
        raise HTTPException(status_code=400, detail="用户已被禁用")
    
    return UserResponse.model_validate(user_db)

async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """获取当前活跃用户"""
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    try:
        user = await AuthService.create_user(db, user_data)
        await db.commit()
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_active_user)):
    """用户登出（前端清除token即可）"""
    return {"message": "登出成功"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    # 获取原始用户对象进行修改
    original_user = await AuthService.get_user_by_username(db, current_user.username)
    if not original_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = await AuthService.update_user(db, original_user, update_data)
    await db.commit()
    return UserResponse.model_validate(updated_user)

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """上传用户头像"""
    try:
        file_path = save_upload_file(file, subfolder="avatars")
        
        # 获取原始用户对象
        original_user = await AuthService.get_user_by_username(db, current_user.username)
        if not original_user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 删除旧头像
        if current_user.avatar_url:
            delete_file(current_user.avatar_url)
        
        # 更新用户头像
        updated_user = await AuthService.update_user(
            db, original_user, {"avatar_url": file_path}
        )
        await db.commit()
        
        return {"avatar_url": file_path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.put("/password")
async def change_password(
    password_data: dict,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="请提供当前密码和新密码")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少6位")
    
    original_user = await AuthService.get_user_by_username(db, current_user.username)
    if not original_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    from app.utils import verify_password, get_password_hash
    if not verify_password(current_password, original_user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    original_user.password_hash = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "密码修改成功"}
