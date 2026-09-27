from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.models import Order
from app.products.service import ProductService
from app.payments.service import charge


class OutOfStockError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class OrderService:
    """
    V1 (this file): a modular monolith. OrderService calls ProductService and
    payments.charge() directly, as plain Python calls, all inside one
    transaction-friendly process. See docs/evolution.md for V2-V6.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.products = ProductService(db)

    async def create_order(self, product_id: int, quantity: int) -> Order:
        product = await self.products.get(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        if not product.in_stock:
            raise OutOfStockError(f"Product {product_id} is out of stock")

        charge_result = charge(order_id=0, amount_cents=product.price_cents * quantity)
        if not charge_result["success"]:
            raise RuntimeError("Payment failed")

        order = Order(product_id=product_id, quantity=quantity, status="paid")
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
