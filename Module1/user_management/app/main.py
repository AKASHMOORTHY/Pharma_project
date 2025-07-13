from fastapi import FastAPI
from user_management.app.routes import user
import uvicorn

app = FastAPI(title="User Management API")

app.include_router(user.router)