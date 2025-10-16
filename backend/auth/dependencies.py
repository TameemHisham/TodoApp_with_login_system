from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from auth.jwt_handler import decode_access_token
from db.db_config import SessionLocal
from enum import Enum
from db.models import Admin as AdminDB, User as UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Extract current user from JWT token."""
    payload = decode_access_token(token)
    username = payload.get("sub")
    user_type = payload.get("type")

    with SessionLocal() as session:
        if user_type == "admin":
            user = session.query(AdminDB).where(
                AdminDB.username == username).first()
        else:
            user = session.query(UserDB).filter(
                UserDB.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(required_role: Role):
    """Dependency factory for role based access control."""
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
