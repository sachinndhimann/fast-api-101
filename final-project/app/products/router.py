from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.products.service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
async def list_products(db: AsyncSession = Depends(get_db)):
    return await ProductService(db).list()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(name: str, price_cents: int, db: AsyncSession = Depends(get_db)):
    return await ProductService(db).create(name, price_cents)

@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await ProductService(db).get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
