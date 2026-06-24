from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database.db import init_db

app = FastAPI(title="ChatLingo")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize the SQLite database and load routers on startup."""
    init_db()

    from routes.screen import router as screen_router
    from routes.history import router as history_router
    from routes.websocket import router as websocket_router

    app.include_router(screen_router)
    app.include_router(history_router)
    app.include_router(websocket_router)
