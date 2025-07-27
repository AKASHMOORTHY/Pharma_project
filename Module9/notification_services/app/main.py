from fastapi import FastAPI
from notification_services.app.database import engine, Base
from notification_services.app.routes import notification

app = FastAPI(title="Notification services")


app.include_router(notification.router)
