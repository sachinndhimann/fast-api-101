from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.products.models import Product

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_id: int) -> Product | None:
        return await self.db.get(Product, product_id)

    async def list(self) -> list[Product]:
        result = await self.db.execute(select(Product))
        return list(result.scalars().all())

    async def create(self, name: str, price_cents: int) -> Product:
        product = Product(name=name, price_cents=price_cents)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product
