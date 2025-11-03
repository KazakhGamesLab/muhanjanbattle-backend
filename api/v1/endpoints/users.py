from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from muhanjanbattle_models.user import UserCreate, UserResponse, UserUpdate
from models.user import User
from core.database import get_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import logging
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        User.__table__.select().where(User.twitch_nickname == user.twitch_nickname)
    )
    if existing.scalar():
        raise HTTPException(status_code=400, detail="Twitch nickname already registered")

    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user



@router.patch("/{telegram_id}", response_model=UserResponse)
async def patch_user_by_telegram_id(
    telegram_id: int,
    user_update: UserUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user_update or user_update.model_dump(exclude_unset=True) == {}:
        return db_user

    update_data = user_update.model_dump(exclude_unset=True)

    if "twitch_nickname" in update_data:
        new_nick = update_data["twitch_nickname"]
        if new_nick != db_user.twitch_nickname:
            existing = await db.execute(
                select(User).where(
                    User.twitch_nickname == new_nick,
                    User.telegram_id != telegram_id  # исключаем самого себя
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=400,
                    detail="Twitch nickname already registered by another user"
                )

    for field, value in update_data.items():
        setattr(db_user, field, value)

    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database integrity error")

    return db_user

@router.get("/{telegram_id}", response_model=UserResponse)
async def read_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    print(user)
    logging.info(f"Found user: {user}")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user