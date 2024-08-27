from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User



async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    user_name: str,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id,
                 user_name=user_name,
                 first_name=first_name,
                 last_name=last_name,
                 phone=phone)
        )
        await session.commit()
        
        
async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()
