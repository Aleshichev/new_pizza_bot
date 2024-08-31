from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Banner

async def orm_add_banner_description(session: AsyncSession, data: list):

    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    for item in data:
        obj = Banner(
            name=item["name"],
            description=item["description"],
        )
        session.add(obj)
    await session.commit()



async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()