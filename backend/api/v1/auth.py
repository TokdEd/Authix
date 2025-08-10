import jwt
import bcrypt
import re
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, validator
from core import config
from db.database import Database, User 

logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 
failed_login_attempts: Dict[str, List[float]] = defaultdict(list)
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

class SecurityConfig:
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 
    MAX_REQUESTS_PER_MINUTE = 60
    
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int
    user_id: int
    username: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    
class PasswordValidator:
    @staticmethod
    def validate_password(password: str) -> str:
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            raise ValueError(f'密碼長度至少需要 {SecurityConfig.MIN_PASSWORD_LENGTH} 個字元')
        if not re.search(r'[A-Z]', password):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not re.search(r'[a-z]', password):
            raise ValueError('密碼必須包含至少一個小寫字母')
        if not re.search(r'\d', password):
            raise ValueError('密碼必須包含至少一個數字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError('密碼必須包含至少一個特殊符號')
        return password

class RateLimiter:
    @staticmethod
    def is_rate_limited(identifier: str, max_requests: int = SecurityConfig.MAX_REQUESTS_PER_MINUTE) -> bool:
        """Check if the identifier is rate limited"""
        now = time.time()
        minute_ago = now - 60
        rate_limit_store[identifier] = [req_time for req_time in rate_limit_store[identifier] if req_time > minute_ago]
        
        # Check if limit exceeded
        if len(rate_limit_store[identifier]) >= max_requests:
            return True
        rate_limit_store[identifier].append(now)
        return False
    
    @staticmethod
    def check_failed_login_attempts(email: str) -> bool:
        """Check if account is locked due to failed login attempts"""
        now = time.time()
        lockout_window = now - SecurityConfig.LOCKOUT_DURATION
        
        failed_login_attempts[email] = [attempt_time for attempt_time in failed_login_attempts[email] if attempt_time > lockout_window]
        
        return len(failed_login_attempts[email]) >= SecurityConfig.MAX_LOGIN_ATTEMPTS
    
    @staticmethod
    def record_failed_login(email: str):
        """Record a failed login attempt"""
        failed_login_attempts[email].append(time.time())
        security_logger.warning(f"Failed login attempt for email: {email}")

class AuthService:
    def __init__(self, db: Database = Depends(Database)):
        self.db = db

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_token(self, user_id: int, token_type: str = "access") -> str:
        expire_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES) if token_type == "access" \
                       else timedelta(days=7)
        expire = datetime.utcnow() + expire_delta
        payload = {
            'user_id': user_id,
            'token_type': token_type,
            'exp': expire,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.ALGORITHM)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token 已過期")
        except jwt.InvalidTokenError:
            raise ValueError("無效的 Token")

async def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(AuthService)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get("user_id")
        if user_id is None or payload.get("token_type") != "access":
            raise credentials_exception
    except (ValueError, jwt.JWTError):
        raise credentials_exception
        
    user = await auth_service.db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, auth_service: AuthService = Depends(AuthService)):
    #DB need dressed as maid 
    existing_user = await auth_service.db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="此電子郵件已被註冊")
    
    try:
        PasswordValidator.validate_password(user_data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    hashed_password = auth_service.hash_password(user_data.password)
    new_user = await auth_service.db.create_user(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password
    )
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: LoginRequest, auth_service: AuthService = Depends(AuthService)):
    """
    使用者登入，成功後返回 access 和 refresh tokens。
    """
    user = await auth_service.db.get_user_by_email(form_data.email)
    if not user or not auth_service.verify_password(form_data.password, user.password):
        # 為了安全，不具體指出是郵箱還是密碼錯誤
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼不正確",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 產生 Access 和 Refresh Token
    access_token = auth_service.create_token(user.id, "access")
    refresh_token = auth_service.create_token(user.id, "refresh")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        username=user.name
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    獲取當前登入使用者的資訊。這是一個受保護的端點。
    """
    return current_user