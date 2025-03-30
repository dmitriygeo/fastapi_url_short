from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import User
from config import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

"""Получение текущего пользователя по токену"""
async def get_current_user(token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)) -> Optional[User]:

    if not token:
        return None
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    print(f"Found user: {user.id if user else None}")
    return user
