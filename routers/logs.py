from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import secrets
from db.database import SessionLocal
from models.models import Logs, Usuarios  # Adjust import as necessary
from utils import create_api_response

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/bitacora/consumidor/{user_id}")
def get_bitacora(user_id: int, page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    offset = (page - 1) * size

    try:
        # Fetch the user for logging purposes
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()

        # Execute the SQL query with pagination
        query = text("""
                    select A.endpoint,
                        A.method,
                        A.codigo_trans,
                        A.fecha_trans,
                        A.usuario,
                        A.UTI
                    from logs_data a
                    order by id desc
                    LIMIT :size OFFSET :offset
        """)
        result = db.execute(query, {"user_id": user_id, "size": size, "offset": offset}).fetchall()

        # Count total records for pagination
        count_query = text("""
            SELECT COUNT(*) 
            FROM logs A
            LEFT JOIN usuarios B ON A.usuario_id = B.id
        """)
        total_records = db.execute(count_query, {"user_id": user_id}).scalar()

        # Convert result to a list of dictionaries
        log_entries = [
            {
                "endpoint": row.endpoint,
                "method": row.method,
                "codigo_trans": row.codigo_trans,
                "fecha_trans": row.fecha_trans,
                "usuario": row.usuario,
                "uti": row.uti                
            }
            for row in result
        ]

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Bitacora obtenida exitosamente",
            information={"bitacora": log_entries, "totalRecords": total_records}
        )

        return response

    except Exception as e:
        db.rollback()

        # Handle the error response
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        
        log_entry = Logs(
            endpoint=f"/api/bitacora/consumidor/{user_id}",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )
