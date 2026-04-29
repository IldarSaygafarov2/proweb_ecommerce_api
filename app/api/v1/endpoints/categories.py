from fastapi import APIRouter, Depends, HTTPException
from app.schemas.categories import CategoryCreateSchema, CategoryUpdateSchema, CategoryReadSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_role
from app.schemas.categories import CategoryReadSchema, CategoryCreateSchema, CategoryUpdateSchema
from app.services.catalog_service import CatalogService
from app.models.enums import UserRole


router = APIRouter(
    tags=['Categories']
)

#

@router.get('/')
async def get_categories(
        db: AsyncSession = Depends(get_db)
) -> list[CategoryReadSchema]:
    categories = await CatalogService(db).list_categories()
    return [CategoryReadSchema.model_validate(category) for category in categories]


@router.post('/', status_code=201)  # api/v1/categories/
async def create_category(
        payload: CategoryCreateSchema,
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
) -> CategoryReadSchema:
    item = await CatalogService(db).create_category(payload)
    return CategoryReadSchema.model_validate(item)


@router.put('/{category_id}')
async def update_category(
        category_id: int,
        payload: CategoryUpdateSchema,
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
) -> CategoryReadSchema:
    item = await CatalogService(db).update_category(category_id, payload)
    return CategoryReadSchema.model_validate(item)


@router.delete('/{category_id}')
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
):
    await CatalogService(db).delete_category(category_id)
