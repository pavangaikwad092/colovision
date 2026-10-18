from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Admin, User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2 = HTTPBearer()


def hash_password(value: str):
    return pwd.hash(value)


def verify_password(raw: str, hashed: str):
    return pwd.verify(raw, hashed)


def create_token(subject: int, role: str):
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.access_token_expire_minutes)
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256"
    )


def current_claims(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2)
):
    try:
        token = credentials.credentials

        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )


def current_user(
    claims=Depends(current_claims),
    db: Session = Depends(get_db)
):
    if claims.get("role") != "user":
        raise HTTPException(
            status_code=403,
            detail="User access required"
        )

    user = db.get(User, int(claims["sub"]))

    if not user or user.status != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail="Approved user access required"
        )

    return user


def current_admin(
    claims=Depends(current_claims),
    db: Session = Depends(get_db)
):
    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required"
        )

    admin = db.get(Admin, int(claims["sub"]))

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Administrator not found"
        )

    return admin