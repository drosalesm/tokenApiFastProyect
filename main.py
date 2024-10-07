from fastapi import FastAPI,Depends, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs,Base
from utils import create_api_response
from schemas import PaisesCreate
from sqlalchemy.orm import Session
from routers import loginlogut, paises,usuarios,gerencias,centroscosto,tokens,roles,permissions,rolepermissions,protected,logs
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI() 


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Add the logging middleware
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)








app.include_router(paises.router, prefix="/api", tags=["Paises"])
app.include_router(usuarios.router, prefix="/api", tags=["Usuarios"])
app.include_router(gerencias.router, prefix="/api", tags=["Gerencias"])
app.include_router(centroscosto.router, prefix="/api", tags=["centros_costo"])
app.include_router(tokens.router, prefix="/api", tags=["tokens"])
app.include_router(roles.router, prefix="/api", tags=["roles"])
app.include_router(permissions.router, prefix="/api", tags=["permissions"])
app.include_router(rolepermissions.router, prefix="/api", tags=["role-permissions"])
app.include_router(loginlogut.router, prefix="/api",tags=["session"])
app.include_router(logs.router, prefix="/api")
app.include_router(protected.router, prefix="/api")


