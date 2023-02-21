from datetime import timedelta

from sqlalchemy.future import select
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = create_async_engine('postgresql+asyncpg://postgres:123456@localhost:5432/vkinder',
                             echo=False,
                             poolclass=NullPool)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    last_action = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    send_notification = Column(Boolean, default=False)


class View(Base):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    viewed_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship(User, backref='views')


class Like(Base):
    __tablename__ = 'like'
    id = Column(Integer, primary_key=True)
    liked_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship(User, backref='likes')


async def is_not_new_user(user_id):
    async with async_session() as session:
        stmt = select(User).where(User.user_id == user_id)
        results = await session.execute(stmt)
        users = results.scalars().all()
    if users:
        return True
    return False


async def is_viewed(user_id, viewed_user_id):
    async with async_session() as session:
        stmt = select(View).where(View.viewed_user == viewed_user_id, View.user_id == user_id)
        results = await session.execute(stmt)
        views = results.scalars().all()
    if views:
        return True
    return False


async def add_new_or_update_user(user_id):
    async with async_session() as session:
        stmt = select(User).where(User.user_id == user_id)
        results = await session.execute(stmt)
        user = results.scalars().first()
        if user:
            user.last_action = func.now()
            user.send_notification = False
            await session.commit()

    if not user:
        user = User(user_id=user_id)
        async with async_session() as session:
            async with session.begin():
                session.add(user)
            await session.commit()


async def add_view(user_id, viewed_user_id):
    view = View(user_id=user_id, viewed_user=viewed_user_id)
    async with async_session() as session:
        async with session.begin():
            session.add(view)
        await session.commit()


async def get_all_users():
    async with async_session() as session:
        stmt = select(User).where(User.last_action + timedelta(minutes=4) < func.now(),
                                  User.send_notification == False)
        results = await session.execute(stmt)
        users = results.scalars().all()
        for user in users:
            user.send_notification = True
        await session.commit()
        return users


async def add_like(user_id, liked_user_id):
    like = Like(user_id=user_id, liked_user=liked_user_id)
    async with async_session() as session:
        async with session.begin():
            session.add(like)
        await session.commit()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
