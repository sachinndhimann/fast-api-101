from fastapi import FastAPI
from app.api.users import router as users_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(users_router)

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}
