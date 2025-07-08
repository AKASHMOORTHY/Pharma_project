from fastapi import FastAPI
from db import Base, engine
from routes import production_routes

app = FastAPI(
    title="PDMS - Production Entry Microservice"
)

Base.metadata.create_all(bind=engine)

app.include_router(production_routes.router)

@app.get("/")
def root():
    return {"message": "Production Entry Service Running"}
