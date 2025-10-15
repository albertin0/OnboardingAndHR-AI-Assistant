from datetime import datetime, timedelta
from passlib.context import CryptContext
from passlib.hash import bcrypt

from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from app.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db import get_session
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

def hash_password(password: str) -> str:
    """
    Hash a password safely with bcrypt.
    Truncate to 72 bytes to avoid ValueError.
    """
    # bcrypt limit = 72 bytes
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        print("⚠️ Warning: Password too long; truncated to 72 bytes for bcrypt compatibility.")
        encoded = encoded[:72]
    safe_password = encoded.decode("utf-8", "ignore")
    return bcrypt.hash(safe_password)

# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_context.verify(plain, hashed)
def verify_password(password: str, hashed: str) -> bool:
    safe_password = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return bcrypt.verify(safe_password, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid JWT token (no subject)")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    session = get_session()
    user = session.exec(select(User).where(User.email == email)).first()
    session.close()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
