import logging
import uuid
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.errors import AppError, NotFoundError, OutOfStockError

logger = logging.getLogger("chapter9")
app = FastAPI(title="Chapter 9 - Error Handling")

PRODUCTS = {1: {"name": "Widget", "in_stock": False}}


def error_envelope(code: str, message: str, request_id: str) -> dict:
    """ONE shape for every error, everywhere -- see chapter 2's error contract."""
    return {"error": {"code": code, "message": message, "request_id": request_id}}


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """
    Handles every custom domain exception in one place. Routes just `raise
    NotFoundError(...)` -- they never construct a JSONResponse themselves.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(exc.code, exc.message, request_id),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Overrides FastAPI's default 422 body shape with OUR envelope, so clients
    get one consistent error shape whether the failure is a Pydantic
    validation error or one of our AppError subclasses.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    first_error = exc.errors()[0] if exc.errors() else {}
    message = f"{'.'.join(str(p) for p in first_error.get('loc', []))}: {first_error.get('msg', 'invalid input')}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_envelope("VALIDATION_ERROR", message, request_id),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all safety net. Logs the FULL exception server-side (for debugging)
    but returns a DELIBERATELY generic message to the client -- see "what NOT
    to expose" below.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception(f"Unhandled exception, request_id={request_id}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_envelope("INTERNAL_ERROR", "An unexpected error occurred", request_id),
    )


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = PRODUCTS.get(product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} does not exist")
    return product


@app.post("/orders")
def create_order(product_id: int, quantity: int):
    product = PRODUCTS.get(product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} does not exist")
    if not product["in_stock"]:
        raise OutOfStockError(f"Product {product_id} is out of stock")
    return {"product_id": product_id, "quantity": quantity}


@app.get("/boom")
def boom():
    """Deliberately raises an unhandled exception, to demonstrate the catch-all handler."""
    return 1 / 0
