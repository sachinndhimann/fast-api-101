"""
Chapter 1 - FastAPI Fundamentals
A minimal but complete CRUD API over an in-memory "Products" store.

Run:
    uvicorn main:app --reload --port 8000
Then open:
    http://localhost:8000/docs      (Swagger UI)
    http://localhost:8000/redoc     (ReDoc)
"""
from __future__ import annotations

from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path, Body, Response, Cookie, Header, status
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI(
    title="Chapter 1 - Products API",
    description="Demonstrates path/query params, request bodies, response models, "
                "status codes, headers, cookies and validation.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory "database". A real app would use SQLAlchemy (see chapter 4).
# We use a plain dict here on purpose: chapter 1 is about HTTP + FastAPI
# mechanics, not persistence.
# ---------------------------------------------------------------------------

DB: dict[int, "Product"] = {}
_next_id = 1


class Category(str, Enum):
    electronics = "electronics"
    grocery = "grocery"
    apparel = "apparel"
    other = "other"


class ProductCreate(BaseModel):
    """What the client sends us to create a product."""
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120, examples=["Wireless Mouse"])
    price_cents: int = Field(gt=0, description="Price in the smallest currency unit (cents/paise)")
    category: Category = Category.other
    in_stock: bool = True


class ProductUpdate(BaseModel):
    """PATCH payload: everything optional, only provided fields are changed."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    price_cents: Optional[int] = Field(default=None, gt=0)
    category: Optional[Category] = None
    in_stock: Optional[bool] = None


class Product(BaseModel):
    """What we store AND what we usually return."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price_cents: int
    category: Category
    in_stock: bool


class ProductOut(Product):
    """
    Separate *output* model from the storage model on purpose. Today they look
    identical, but this is the seam where you'd hide internal fields (e.g. a
    cost_price the client should never see) without touching the storage model.
    """
    pass


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductOut], tags=["products"])
def list_products(
    category: Optional[Category] = Query(None, description="Filter by category"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    limit: int = Query(20, ge=1, le=100, description="Max items to return"),
    offset: int = Query(0, ge=0, description="Items to skip"),
):
    """
    GET is for reading. It must never change server state and must be safe to
    call repeatedly (idempotent AND safe). All filtering/paging happens via
    query parameters, never via the request body -- GET requests conventionally
    have no body, and many HTTP clients/proxies will drop it if you add one.
    """
    items = list(DB.values())
    if category is not None:
        items = [p for p in items if p.category == category]
    if in_stock is not None:
        items = [p for p in items if p.in_stock == in_stock]
    return items[offset : offset + limit]


@app.get("/products/{product_id}", response_model=ProductOut, tags=["products"])
def get_product(product_id: int = Path(..., gt=0, description="The product's numeric id")):
    product = DB.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@app.post(
    "/products",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
)
def create_product(payload: ProductCreate, response: Response):
    """
    POST creates a new resource. It is neither safe nor idempotent: calling it
    twice creates two products. Correct status code on success is 201, and we
    set a Location header pointing at the new resource -- most APIs skip this,
    but it's part of doing REST properly (see chapter 2).
    """
    global _next_id
    product = Product(id=_next_id, **payload.model_dump())
    DB[product.id] = product
    _next_id += 1
    response.headers["Location"] = f"/products/{product.id}"
    return product


@app.put("/products/{product_id}", response_model=ProductOut, tags=["products"])
def replace_product(product_id: int, payload: ProductCreate):
    """
    PUT replaces the *entire* resource. It IS idempotent: calling it twice with
    the same body leaves the server in the same state. Contrast with PATCH
    below. If the resource doesn't exist, many APIs choose to create it (also
    idempotent) -- here we choose to 404 to keep id assignment centralized in POST.
    """
    if product_id not in DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product = Product(id=product_id, **payload.model_dump())
    DB[product_id] = product
    return product


@app.patch("/products/{product_id}", response_model=ProductOut, tags=["products"])
def update_product(product_id: int, payload: ProductUpdate):
    """
    PATCH applies a *partial* update. Only fields the client actually sent are
    changed. This is why ProductUpdate has every field Optional: `None` means
    "client didn't mention this field", not "set it to null".
    """
    product = DB.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    updates = payload.model_dump(exclude_unset=True)
    updated = product.model_copy(update=updates)
    DB[product_id] = updated
    return updated


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["products"])
def delete_product(product_id: int):
    """
    DELETE is idempotent: deleting an already-deleted resource should not be
    treated as an error by a well-behaved client, even though we 404 here on
    the *first* miss. 204 No Content means "worked, nothing to return".
    """
    if product_id not in DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    del DB[product_id]
    return None


# ---------------------------------------------------------------------------
# Headers & cookies demo -- these show up constantly in real APIs
# (API keys, request IDs, session cookies) so we make them explicit here.
# ---------------------------------------------------------------------------

@app.get("/whoami", tags=["meta"])
def whoami(
    response: Response,
    x_api_key: Optional[str] = Header(None, description="Example custom header"),
    session_id: Optional[str] = Cookie(None),
):
    if session_id is None:
        session_id = "demo-session-abc123"
        response.set_cookie("session_id", session_id, max_age=3600, httponly=True)
    return {"api_key_seen": x_api_key, "session_id": session_id}


@app.post("/products/bulk", response_model=list[ProductOut], tags=["products"])
def bulk_create(payload: list[ProductCreate] = Body(..., min_length=1, max_length=50)):
    """Demonstrates a request body that is a JSON array, with length validation."""
    global _next_id
    created = []
    for item in payload:
        product = Product(id=_next_id, **item.model_dump())
        DB[product.id] = product
        _next_id += 1
        created.append(product)
    return created
