from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app.db.session import get_db
from app.models.models import User, Link
from app.schemas.schemas import LinkCreate, Link as LinkSchema, UserCreate, Token
from app.auth.auth_secuirity import get_password_hash, create_access_token, verify_password
from app.utils.utils_url import generate_short_code, is_link_expired, get_default_expiry
from app.redis.redis import get_redis
import redis.asyncio as redis
import json
from urllib.parse import unquote
from app.api.api_utils import model_to_dict
from app.auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth_secuirity import authenticate_user

router = APIRouter()

""""Регистрация пользователя"""
@router.post("/users/", response_model=Token)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Создаем нового пользователя
    db_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Создаем токен
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# @router.post("/token", response_model=Token)
# async def login_for_access_token(email: str, password: str, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()
#
#     if not user or not verify_password(password, user.hashed_password):
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})

    # Возвращаем токен, который будет автоматически использоваться для следующих запросов
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/links/shorten", response_model=LinkSchema)
async def create_short_link(
        link: LinkCreate,
        db: AsyncSession = Depends(get_db),
        redis_client: redis.Redis = Depends(get_redis),
        current_user: Optional[User] = Depends(get_current_user)
):
    print(f"Current user: {current_user.id if current_user else None}")
    # Проверяем custom_alias если он предоставлен
    if link.custom_alias:
        # Проверяем существование алиаса в базе данных
        result = await db.execute(
            select(Link).where(
                (Link.short_code == link.custom_alias) |
                (Link.custom_alias == link.custom_alias)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Custom alias already exists"
            )
        short_code = link.custom_alias
    else:
        # Генерируем уникальный короткий код
        attempt = 0
        while True:
            if attempt > 5:  # Ограничиваем количество попыток
                raise HTTPException(
                    status_code=500,
                    detail="Could not generate unique short code"
                )

            short_code = generate_short_code(str(link.original_url) + str(attempt))

            # Проверяем существование кода
            result = await db.execute(
                select(Link).where(Link.short_code == short_code)
            )
            if not result.scalar_one_or_none():
                break

            attempt += 1

    expires_at = link.expires_at or (datetime.now(timezone.utc) + timedelta(days=30))
    # Создаем новую ссылку
    new_link = Link(
        original_url=str(link.original_url),
        short_code=short_code,
        custom_alias=link.custom_alias,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        user_id=current_user.id if current_user else None
    )

    try:
        db.add(new_link)
        await db.commit()
        await db.refresh(new_link)

        # Кэшируем в Redis
        await redis_client.set(
            f"link:{short_code}",
            str(link.original_url),
            ex=30
        )

        return new_link

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not create link"
        )
        # if "short_code" in str(e.orig):
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Short code already exists"
        #     )
        # elif "custom_alias" in str(e.orig):
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Custom alias already exists"
        #     )
        # else:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Database integrity error"
        #     )

async def clean_expire_link(db: AsyncSession, redis_client: redis.Redis = Depends(get_redis)):
    try:
        current_time = datetime.now(timezone.utc)

        # Получаем истекшие ссылки
        result = await db.execute(
            select(Link).where(
                (Link.expires_at <= current_time) &
                (Link.expires_at.isnot(None))
            )
        )
        expired_links = result.scalars().all()

        # Удаляем их из Redis и базы данных
        for link in expired_links:
            await redis_client.delete(f"link:{link.short_code}")

        await db.execute(
            delete(Link).where(
                (Link.expires_at <= current_time) &
                (Link.expires_at.isnot(None))
            )
        )
        await db.commit()

    except Exception as e:
        await db.rollback()

@router.get('/{short_code}')
async def redirect_url(short_code: str, db: AsyncSession = Depends(get_db),
                       redis_client: redis.Redis = Depends(get_redis)):
    cache_url = await redis_client.get(f"link: {short_code}")
    if cache_url:
        return {'url': cache_url}

    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404,
                            detail='link not found')
    # if is_link_expired(link.expires_at):
    #     raise HTTPException(status_code=410,
    #                         detail='link has expired')
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        await db.delete(link)
        await db.commit()
        raise HTTPException(
            status_code=410,
            detail="Link has expired"
        )

    link.last_accessed = datetime.now(timezone.utc)
    link.access_count += 1
    await db.commit()
    if link.expires_at:
        await redis_client.set(
            f"link:{short_code}",
            link.original_url,
            ex=30
        )
    return {'url': link.original_url}

@router.get("/links/{short_code}/stats", response_model=LinkSchema)
async def get_link_stats(short_code: str, db: AsyncSession = Depends(get_db),
                         current_user: Optional[User] = Depends(get_current_user)):
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if current_user and link.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    return link

@router.delete("/links/{short_code}")
async def delete_link(short_code: str, db: AsyncSession = Depends(get_db),
                      redis_client: redis.Redis = Depends(get_redis),
                      current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    await db.delete(link)
    await db.commit()

    await redis_client.delete(f"link:{short_code}")

    return {"message": "link deleted"}

@router.put("/links/{short_code}")
async def update_link(short_code: str, new_link: LinkCreate,
                      db: AsyncSession = Depends(get_db),
                      redis_client: redis.Redis = Depends(get_redis),
                      current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )

    link.original_url = str(new_link.original_url)
    if new_link.expires_at:
        link.expires_at = new_link.expires_at

    await db.commit()
    await db.refresh(link)

    # Обновляем кэш
    await redis_client.set(
        f"link:{short_code}",
        str(new_link.original_url),
        ex=30
    )

    return link


@router.get("/links/search", response_model=List[LinkSchema])
async def search_links(
        original_url: str = Query(..., description="URL"),
        db: AsyncSession = Depends(get_db),
        redis_client: redis.Redis = Depends(get_redis)
):
    # Пробуем получить результат из кэша
    cache_key = f"search:{original_url}"
    cached_result = await redis_client.get(cache_key)

    if cached_result:
        return json.loads(cached_result)

    # Если в кэше нет, ищем в базе данных
    decoded_url = unquote(original_url)

    try:
        result = await db.execute(
            select(Link)
                .where(Link.original_url == decoded_url)
                .order_by(Link.created_at.desc())
        )
        links = result.scalars().all()

        if not links:
            raise HTTPException(
                status_code=404,
                detail="No links found for this URL"
            )

        # Кэшируем результат
        links_data = [model_to_dict(link) for link in links]
        await redis_client.set(
            cache_key,
            json.dumps(links_data, default=str),
            ex=30
        )

        return links

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error occurred while searching for links"
        )