from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from app.models import User
from app.schemas import UserCreate
from app.utils import get_password_hash, verify_password, _truncate_password

class AuthService:
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """创建新用户"""
        try:
            # 检查用户名是否已存在
            existing_user = await AuthService.get_user_by_username(db, user_data.username)
            if existing_user:
                raise ValueError("用户名已存在")
            
            # 检查邮箱是否已存在
            if user_data.email:
                existing_email = await AuthService.get_user_by_email(db, user_data.email)
                if existing_email:
                    raise ValueError("邮箱已被注册")
            
            # 创建用户
            # 确保密码处理符合bcrypt限制
            password_str = str(user_data.password)
            import logging
            
            # 截断密码到72字节（bcrypt限制）
            password_str = _truncate_password(password_str)
            
            if not password_str:
                raise ValueError("密码不能为空或包含无效字符")
                
            hashed_password = get_password_hash(password_str)
            
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                phone=user_data.phone,
                password_hash=hashed_password
            )
            db.add(db_user)
            await db.flush()
            return db_user
        except ValueError:
            # 重新抛出ValueError用于业务错误
            raise
        except Exception as e:
            # 记录bcrypt或密码处理错误
            import traceback
            print(f"创建用户时出现错误: {str(e)}")
            print(traceback.format_exc())
            raise ValueError(f"密码处理错误: {str(e)}")
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = await AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
        """更新用户信息"""
        for field, value in update_data.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        await db.flush()
        return user
