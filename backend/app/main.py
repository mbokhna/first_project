from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import db
from app.config import ENV_FILE, STATIC_DIR, get_session_secret
from app.routers import ai, auth, board

load_dotenv(ENV_FILE)


def _init_db() -> None:
    conn = db.get_connection()
    try:
        db.init_db(conn)
    finally:
        conn.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Project Management App")

    app.add_middleware(SessionMiddleware, secret_key=get_session_secret())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _init_db()

    app.include_router(auth.router)
    app.include_router(board.router)
    app.include_router(ai.router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
