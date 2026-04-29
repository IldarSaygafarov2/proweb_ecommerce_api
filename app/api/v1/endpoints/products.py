from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, File, Query, Form, UploadFile, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_role, get_current_user
from app.core.config import settings
from app.models.enums import UserRole
from app.models.user import User
from app.core.media import save_product_image
from app.services.catalog_service import CatalogService
from app.schemas.products import ProductUpdateSchema, ProductCreateSchema, ProductReadSchema
from app.services.product_comment_service import ProductCommentService
from app.schemas.product_comment import ProductCommentRead, ProductCommentCreate

router = APIRouter(
    tags=['Products']
)

# http://127.0.0.1:8000/api/v1/products/?search=product
@router.get('/')
@settings.rate_limiter.limit('120/minute')
async def get_products(
        request: Request,
        search: str | None = Query(default=None),
        category_id: int | None = Query(default=None),
        db: AsyncSession = Depends(get_db)
) -> list[ProductReadSchema]:
    items = await CatalogService(db).list_products(search, category_id)
    return [ProductReadSchema.model_validate(item) for item in items]


@router.get('/{product_id}', response_model=ProductReadSchema)
async def get_product_detail(product_id: int, db:AsyncSession = Depends(get_db)):
    product = await CatalogService(db).get_product(product_id)
    return ProductReadSchema.model_validate(product)


@router.post('/', status_code=201)
async def create_product(
        name: str = Form(...),
        price: Decimal = Form(...),
        stock: int = Form(...),
        category_id: int = Form(...),
        description: str | None = Form(default=None),
        image: UploadFile | None = File(default=None),
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
) -> ProductReadSchema:
    image_url = await save_product_image(image) if image else None
    payload = ProductCreateSchema(
        name=name,
        description=description,
        image_url=image_url,
        price=price,
        stock=stock,
        category_id=category_id
    )
    item = await CatalogService(db).create_product(payload)
    return ProductReadSchema.model_validate(item)


@router.put('/{product_id}')
async def update_product(
        product_id: int,
        name: str | None = Form(default=None),
        price: Decimal | None = Form(default=None),
        stock: int | None = Form(default=None),
        category_id: int | None = Form(default=None),
        description: str | None = Form(default=None),
        image: UploadFile | None = File(default=None),
        remove_image: bool = Form(default=False),
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
) -> ProductReadSchema:
    payload_data = {}
    if name is not None:
        payload_data['name'] = name
    if description is not None:
        payload_data['description'] = description
    if price is not None:
        payload_data['price'] = price
    if stock is not None:
        payload_data['stock'] = stock
    if category_id is not None:
        payload_data['category_id'] = category_id
    if image is not None:
        payload_data['image_url'] = await save_product_image(image)
    elif remove_image:
        payload_data['image_url'] = None

    payload = ProductUpdateSchema(**payload_data)
    # print(payload_data)

    item = await CatalogService(db).update_product(product_id, payload)
    return ProductReadSchema.model_validate(item)


@router.delete('/{product_id}')
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        _: object = Depends(require_role(UserRole.admin))
) -> Response:
    await CatalogService(db).delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{product_id}/comments')
async def get_product_comments(
        product_id: int,
        db: AsyncSession = Depends(get_db),
) -> list[ProductCommentRead]:
    return await ProductCommentService(db).list_for_product(product_id)


@router.post('/{product_id}/comments')
async def create_comment_for_product(
        product_id: int,
        payload: ProductCommentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> ProductCommentRead:
    return await ProductCommentService(db).create(product_id=product_id, user_id=current_user.id, payload=payload)


@router.delete('/{product_id}/comments/{comment_id}')
async def delete_comment(
        product_id: int,
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Response:
    is_admin = current_user.role == UserRole.admin
    await ProductCommentService(db).delete(comment_id=comment_id, is_admin=is_admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# TODO: проверить удаление фотографии продукта при обновлении продукта