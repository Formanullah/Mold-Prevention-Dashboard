from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import data, alerts, errors, health, nodes


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="AERIS Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(data.router)
    app.include_router(alerts.router)
    app.include_router(errors.router)
    app.include_router(health.router)
    app.include_router(nodes.router)

    return app


app = create_app()
