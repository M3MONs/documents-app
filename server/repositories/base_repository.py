from typing import Sequence, TypeVar, Type, Any
from sqlalchemy import Boolean, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.pagination import PaginationResponse

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
        model: Type[M],
        db: AsyncSession,
        item_schema: Type[Any] | None = None,
        offset: int = 0,
        limit: int = 100,
        ordering: str | None = None,
        ordering_desc: bool = False,
        filters: list[tuple[str, Any]] | None = None,
    ) -> PaginationResponse:
        query = select(model)
        total_query = select(func.count()).select_from(model)

        if filters:
            for field, value in filters:
                print(f"Applying filter on field: {field} with value: {value}", value in (1, '1', 'yes', 'Yes', 'YES', True, 'true', 'True', 'TRUE'))
                column = getattr(model, field)
                if isinstance(column.type, Boolean):
                    if value in (1, '1', 'yes', 'Yes', 'YES', 'true', 'True', 'TRUE'):
                        bool_value = True
                    else:
                        bool_value = False
                    query = query.where(column == bool_value)
                    total_query = total_query.where(column == bool_value)
                else:
                    query = query.where(column.ilike(f"%{value}%"))
                    total_query = total_query.where(column.ilike(f"%{value}%"))

        if ordering:
            column = getattr(model, ordering)
            query = query.order_by(column.desc() if ordering_desc else column)
        
        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        total_result = await db.execute(total_query)
        
        total = total_result.scalar_one()

        items = result.scalars().all()

        if item_schema:
            items = [item_schema.from_orm(item) for item in items]

        return PaginationResponse(total=total, items=list(items))

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
    async def delete(model: Type[M], db: AsyncSession, entity_id: str) -> bool:
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
