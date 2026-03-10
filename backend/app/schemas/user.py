from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v == '' or v is None:
            return None
        # 简单的邮箱格式验证
        if v and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # bcrypt 限制密码最长 72 字节，中文每个字符占 3 字节
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            # 截断到 72 字节
            truncated = password_bytes[:72]
            # 确保不会截断在多字节字符中间
            while len(truncated) > 0:
                try:
                    return truncated.decode('utf-8')
                except UnicodeDecodeError:
                    truncated = truncated[:-1]
            return v[:24]  # 最坏情况，只取前 24 个字符
        return v

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_update(cls, v):
        if v == '' or v is None:
            return None
        if v and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str]
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
