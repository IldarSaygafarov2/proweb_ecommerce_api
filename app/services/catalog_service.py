from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.categories import CategoryUpdateSchema, CategoryCreateSchema
from app.repositories.category_repo import CategoryRepository
from app.repositories.products_repo import ProductRepository
from app.models.category import Category
from app.models.product import Product
from app.schemas.products import ProductCreateSchema, ProductUpdateSchema
from app.core.slug import make_unique_slug
from slugify import slugify
from app.core.media import remove_local_media_file
from app.services.cache import get_json, set_json, delete_by_prefix


class CatalogService:
    def __init__(self, session: AsyncSession):
        self.category_repo = CategoryRepository(session)
        self.products_repo = ProductRepository(session)

    async def list_categories(self) -> list[Category]:
        return await self.category_repo.list()

    async def create_category(self, category: CategoryCreateSchema) -> Category:
        data = Category(name=category.name, description=category.description)
        created = await self.category_repo.create(data)
        await delete_by_prefix('categories:')
        return created

    async def update_category(self, category_id: int, payload: CategoryUpdateSchema) -> Category:
        category = await self.category_repo.get(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if payload.name is not None:
            category.name = payload.name
        if payload.description is not None:
            category.description = payload.description

        updated = await self.category_repo.update(category)
        await delete_by_prefix('categories:')
        return updated

    async def delete_category(self, category_id: int) -> None:
        category = await self.category_repo.get(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await self.category_repo.delete(category)
        await delete_by_prefix('categories:')

    async def list_products(self, search: str | None, category_id: int | None) -> list[Product]:
        cache_key = f'products:list:{search or ""}:{category_id or 0}'
        cached = await get_json(cache_key)
        if cached:
            return [Product(**item) for item in cached]  # name=, price=

        items = await self.products_repo.list(search, category_id)
        await set_json(cache_key, [self._product_to_dict(product) for product in items])
        return items

    async def get_product(self, product_id: int) -> Product:
        cache_key = f'products:detail:{product_id}'
        cached = await get_json(cache_key)
        if cached:
            return Product(**cached)

        product = await self.products_repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
        await set_json(cache_key, self._product_to_dict(product))
        return product

    async def create_product(self, payload: ProductCreateSchema) -> Product:
        existing_slugs = await self.products_repo.get_existing_slugs()
        base_slug = slugify(payload.name)
        slug = make_unique_slug(base_slug, existing_slugs)
        product_data = payload.model_dump()
        product_data['slug'] = slug
        product = Product(**product_data)
        created = await self.products_repo.create(product)

        await delete_by_prefix('products:list:')
        await delete_by_prefix(f'products:detail:{created.id}')

        return created

    async def update_product(self, product_id: int, payload: ProductUpdateSchema) -> Product:
        product = await self.products_repo.get(product_id)
        if not product:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

        old_image_url = product.image_url
        update_data = payload.model_dump(exclude_unset=True)
        print(update_data)
        if "name" in update_data:
            existing_slugs = await self.products_repo.get_existing_slugs()
            base_slug = slugify(update_data['name'])
            update_data['slug'] = make_unique_slug(base_slug, existing_slugs)

        for key, value in update_data.items():
            setattr(product, key, value)

        updated = await self.products_repo.update(product)
        if old_image_url != updated.image_url:
            remove_local_media_file(old_image_url)

        await delete_by_prefix('products:list:')
        await delete_by_prefix(f'products:detail:{updated.id}')

        return updated

    async def delete_product(self, product_id: int) -> None:
        product = await self.products_repo.get(product_id)
        if not product:
            raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')

        remove_local_media_file(product.image_url)
        await self.products_repo.delete(product)
        await delete_by_prefix('products:list:')
        await delete_by_prefix(f'products:detail:{product.id}')


    @staticmethod
    def _product_to_dict(product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "image_url": product.image_url,
            "price": product.price,
            "stock": product.stock,
            "category_id": product.category_id
        }
