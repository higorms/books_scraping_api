from fastapi import FastAPI
import uvicorn
from src.app.routes.book_routes import router as book_router

app = FastAPI(title="Books API")

app.include_router(book_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=8000, reload=True)
