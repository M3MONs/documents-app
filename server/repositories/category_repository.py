from typing import Sequence
from sqlalchemy import select, exists, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category, category_department_visibility
from models.user import user_departments


class CategoryRepository:
    @staticmethod
    async def get_categories_for_user_in_organization(
        db: AsyncSession, user_id: str, organization_id: str
    ) -> Sequence[Category]:
        user_departments_subquery = (
            select(user_departments.c.department_id).where(user_departments.c.user_id == user_id).subquery()
        )

        stmt = (
            select(Category)
            .where(Category.organization_id == organization_id)
            .where(
                or_(
                    ~exists(
                        select(1)
                        .select_from(category_department_visibility)
                        .where(category_department_visibility.c.category_id == Category.id)
                    ),
                    exists(
                        select(1)
                        .select_from(category_department_visibility)
                        .where(
                            and_(
                                category_department_visibility.c.category_id == Category.id,
                                category_department_visibility.c.department_id.in_(
                                    select(user_departments_subquery.c.department_id)
                                ),
                            )
                        )
                    ),
                )
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def is_unique_category_name_in_organization(db: AsyncSession, organization_id: str, name: str) -> bool:
        stmt = select(exists().where(and_(Category.organization_id == organization_id, Category.name.ilike(name))))
        result = await db.execute(stmt)
        return not result.scalar()
    
    @staticmethod
    async def validate_unique_name_on_update(db: AsyncSession, category_id: str, new_name: str) -> bool:
        stmt = select(exists().where(
            and_(
                Category.name == new_name,
                Category.id != category_id
            )
        ))
        result = await db.execute(stmt)
        return not result.scalar()
