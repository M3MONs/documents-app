from typing import Sequence, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")


class NotFoundError(Exception):
    pass


class BaseRepository:
    @staticmethod
    async def get_by_id(model: Type[M], db: AsyncSession, entity_id: str) -> M | None:
        obj = await db.get(model, entity_id)
        return obj

    @staticmethod
    async def get_all(model: Type[M], db: AsyncSession) -> Sequence[M]:
        result = await db.execute(select(model))
        return result.scalars().all()

    @staticmethod
    async def get_paginated(
        model: Type[M], db: AsyncSession, offset: int = 0, limit: int = 100, ordering: str | None = None
    ) -> Sequence[M]:
        query = select(model).offset(offset).limit(limit)
        if ordering:
            query = query.order_by(ordering)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, entity: M) -> M:
        try:
            db.add(entity)
            await db.commit()
            await db.refresh(entity)
            return entity
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update(db: AsyncSession, entity: M) -> M:
        try:
            await db.merge(entity)
            await db.commit()
            await db.refresh(entity)
            return entity
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete(model: Type[M], db: AsyncSession, entity_id: int) -> bool:
        obj = await db.get(model, entity_id)
        if obj is None:
            raise NotFoundError(f"{model.__name__} with id {entity_id} not found")
        try:
            await db.delete(obj)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def bulk_create(db: AsyncSession, entities: list[M]) -> list[M]:
        try:
            db.add_all(entities)
            await db.commit()

            for entity in entities:
                await db.refresh(entity)

            return entities
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def bulk_update(db: AsyncSession, entities: list[M]) -> list[M]:
        try:
            for entity in entities:
                await db.merge(entity)

            await db.commit()

            for entity in entities:
                await db.refresh(entity)

            return entities
        except Exception as e:
            await db.rollback()
            raise e
