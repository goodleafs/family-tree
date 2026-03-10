from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
import warnings
# 禁用可能导致问题的警告
warnings.filterwarnings('ignore')

# 尝试直接使用bcrypt进行操作以避开初始化时的问题
import bcrypt

def _truncate_password(password: str) -> str:
    """截断密码到72字节（bcrypt限制）"""
    if not password:  # 检查是否为None或空值
        return ""
    
    # 尝试UTF-8编码截断
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # 截断到72字节，并确保不会截断在多字节字符中间
        truncated = password_bytes[:72]
        # 递减直到可以解码
        while len(truncated) > 0:
            try:
                result = truncated.decode('utf-8')
                return result
            except UnicodeDecodeError:
                truncated = truncated[:-1]
        # 如果完全无法解码，则截取前几个字符
        return password[:24]
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    if not plain_password or not hashed_password:
        return False
    
    try:
        # 截断明文密码（符合bcrypt要求）
        processed_password = _truncate_password(plain_password)
        # 使用bcrypt直接验证
        return bcrypt.checkpw(processed_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password) -> str:
    """生成密码哈希，自动截断到72字节（bcrypt限制）"""
    # 首先强制转换为字符串
    password_str = str(password)
    
    # 截断密码以符合bcrypt 72字节限制
    password_str = _truncate_password(password_str)
    
    if not password_str:
        raise ValueError("密码不能为空或者全是非法字符")
    
    # 使用bcrypt直接生成哈希
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_str.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """验证JWT令牌"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username_value: Optional[str] = payload.get("sub")
        if not username_value:
            return None
        return username_value
    except JWTError:
        return None
