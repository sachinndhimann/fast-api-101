from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.orders.service import OrderService, OutOfStockError, ProductNotFoundError

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(product_id: int, quantity: int, db: AsyncSession = Depends(get_db)):
    try:
        order = await OrderService(db).create_order(product_id, quantity)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except OutOfStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return order
