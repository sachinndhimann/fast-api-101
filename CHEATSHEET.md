# Cheatsheet

## FastAPI basics

```python
from fastapi import FastAPI, Depends, HTTPException, status, Query, Path, Body
from pydantic import BaseModel

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int = Path(..., gt=0), q: str | None = Query(None, max_length=50)):
    ...

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    ...
```

## Pydantic v2

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # replaces orm_mode
    id: int
    email: str
```

## Dependency injection

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    ...
```

## JWT lifecycle

```
login -> verify password -> sign JWT (exp, sub, iat) -> return access + refresh token
request -> Authorization: Bearer <token> -> decode + verify signature + check exp -> current_user
refresh -> verify refresh token -> issue new access token (rotate refresh token)
```

## SQLAlchemy 2.0 async

```python
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

## Alembic

```bash
alembic init alembic
alembic revision --autogenerate -m "create users table"
alembic upgrade head
alembic downgrade -1
```

## Redis caching

```python
key = f"product:{product_id}"
cached = await redis.get(key)
if cached:
    return json.loads(cached)
data = await fetch_from_db(product_id)
await redis.set(key, json.dumps(data), ex=300)  # TTL 5 min
```

## Rate limiting (token bucket, conceptually)

```
tokens = min(capacity, tokens + elapsed_time * refill_rate)
if tokens >= 1: tokens -= 1; allow
else: reject (429)
```

## RabbitMQ

```python
# producer
channel.basic_publish(exchange="orders", routing_key="order.created", body=payload)

# consumer
channel.basic_consume(queue="order_created_q", on_message_callback=handle, auto_ack=False)
channel.basic_ack(delivery_tag)  # only after successful processing
```

## Kafka

```python
# producer
producer.produce("orders", key=str(order_id), value=json.dumps(payload))
producer.flush()

# consumer
consumer.subscribe(["orders"])
msg = consumer.poll(1.0)
consumer.commit(msg)  # after processing, for at-least-once semantics
```

## HTTP status codes you should use on purpose

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST that creates a resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request, business-rule violation |
| 401 | Unauthorized | Missing/invalid credentials |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource, version conflict |
| 422 | Unprocessable Entity | Validation error (FastAPI default) |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Unhandled exception |
| 503 | Service Unavailable | Dependency down, health check failing |

## Testing

```python
from fastapi.testclient import TestClient

app.dependency_overrides[get_db] = override_get_db

def test_create_user():
    resp = client.post("/users", json={"email": "a@b.com", "name": "A"})
    assert resp.status_code == 201
```

## Docker / Uvicorn / Gunicorn

```bash
uvicorn main:app --reload                       # dev
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000   # prod
```
