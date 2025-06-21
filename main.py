from fastapi import FastAPI
from routers import user_routes
from routers import auth_routes
from db.postgres import init_db
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.sync_to_keycloak import sync_users_to_keycloak
import asyncio
from logs.logging_config import setup_logger


app = FastAPI(title="User Info Microservice")

init_db()
setup_logger()

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(auth_routes.router, prefix="/auth")


# Background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(sync_users_to_keycloak()), "interval", seconds=15)
scheduler.start()