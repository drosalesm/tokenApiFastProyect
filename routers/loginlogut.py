from fastapi import APIRouter, Depends, HTTPException, status, Request, Response,Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from models.models import Usuarios,Logs
from schemas import LoginRequest,TokenResponse
from utils import verify_password
from db.database import engine,SessionLocal
from auth import create_access_token
from datetime import datetime, timedelta


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)) -> JSONResponse:
    
    uti = secrets.token_hex(16)    
    user = db.query(Usuarios).filter(Usuarios.usuario == login_request.usuario).first()
    if user and verify_password(login_request.password, user.password):
        access_token_expires = timedelta(hours=1)
        access_token = create_access_token(data={"sub": user.usuario}, expires_delta=access_token_expires)
        
        # Extract role name assuming user.role is an object with a 'name' attribute
        user_role_name = user.role.name if user.role and hasattr(user.role, 'name') else 'Unknown Role'

    
        log_entry = Logs(
            endpoint=f"/login/",
            method="POST",
            request_body=user_role_name,
            response_body=access_token,
            status_code=200,
            transaction_id=uti,
            usuario_id=user.id
        )
        db.add(log_entry)
        db.commit()

        
        return JSONResponse(
            content={
                "TokenAcceso": access_token,
                "token_type": "bearer",
                "userId": user.id,
                "userName": user.nombres,
                "userRole": user.role_id,
                "userRoleName": user_role_name
            }                        
        )
    
            
    
    raise HTTPException(status_code=401, detail="Credenciales Invalidas")


@router.post("/logout")
def logout(request: Request) -> JSONResponse:
    uti = secrets.token_hex(16)      
    log_entry = Logs(
            endpoint=f"/logout/",
            method="POST",
            request_body='',
            response_body='',
            status_code=200,
            transaction_id=uti,
            usuario_id=''
        )
    
    
    return JSONResponse(content={"detail": "Successfully logged out"})