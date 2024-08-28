from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.user import User
from src.models.role import Role
from src.schemas.user import UserCreate, UserInDB

async def create_user_service(user_create: UserCreate, db: AsyncSession) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    subscriber_role = await get_or_create_subscriber_role(db)

    if subscriber_role not in user.roles:
        user.roles.append(subscriber_role)
        await db.commit()
        await db.refresh(user)

    return user

async def get_or_create_subscriber_role(db: AsyncSession) -> Role:
    result = await db.execute(select(Role).filter_by(name='subscriber'))
    subscriber_role = result.scalars().first()

    if not subscriber_role:
        await seed_roles(db)
        result = await db.execute(select(Role).filter_by(name='subscriber'))
        subscriber_role = result.scalars().first()

    return subscriber_role

async def seed_roles(db: AsyncSession):
    roles = ['subscriber', 'premium', 'admin']
    existing_roles = await db.execute(select(Role.name))
    existing_role_names = {row[0] for row in existing_roles}

    for role_name in roles:
        if role_name not in existing_role_names:
            db.add(Role(name=role_name))
    await db.commit()
