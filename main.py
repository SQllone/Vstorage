from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routers import auth, users, categories, products, suppliers, orders
from app.rate_limiter import limiter

app = FastAPI(
    title="VStorage - Система управления складом",
    description="FastAPI приложение для управления складскими операциями",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])


@app.get("/")
async def root():
    return {
        "message": "VStorage API - Система управления складом",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VStorage API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
