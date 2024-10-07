from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Logs, Tokens as tokensModel,SeriesToken,Usuarios,has_permission
from utils import create_api_response,hash_nombre,decrypt_data,encrypt_data
from schemas import GerenciasCreate,CentrosCostoCreate,TokensCreate,TokenUpdate
from sqlalchemy.orm import Session
import json
import secrets
from sqlalchemy import text





def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()










@router.get("/tokens/consumidor/{user_id}")
def get_all_tokens(user_id: int,db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    
    try:


        permiso='Visualizar informacion'

        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()


        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  # Adjust the endpoint as needed
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti,
                usuario_id=user_id 
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response
        
        tokens = db.query(tokensModel).all()
        tokens_list = [token.to_dict() for token in tokens]

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Tokens obtenidos exitosamente",
            information=tokens_list
        )

        log_entry = Logs(
            endpoint="/api/tokens/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except Exception as e:
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/tokens/",
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







@router.post("/tokens/consumidor/{user_id}", response_model=dict)
def create_token(user_id: int,token: TokensCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:


        permiso='crear informacion'

        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()


        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  # Adjust the endpoint as needed
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti,
                usuario_id=user_id 
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response


        encrypted_numero_serie = encrypt_data(token.numero_serie)

        # Check if the related usuario exists if provided
        if token.usuario_id:
            usuario = db.query(Usuarios).filter(Usuarios.id == token.usuario_id).first()
            if not usuario:
                response = create_api_response(
                    uti=uti,
                    status="error",
                    code=404,
                    message=f"Usuario con ID {token.usuario_id} no encontrado"
                )
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])


        
        print('Viendo los valores del token',)
        
        db_token = tokensModel(
            numero_serie=encrypted_numero_serie,
            estado=token.estado,
            tipo_token=token.tipo_token,
            usuario_id=token.usuario_id,
            serie_token_id=token.serie_token_id
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message="Token creado exitosamente",
            information={"id": db_token.id}
        )

        # Log the request and response
        log_entry = Logs(
            endpoint="/api/tokens/",
            method="POST",
            request_body=token.json(),
            response_body=json.dumps(response),
            status_code=201,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle and log HTTP errors (404)
        db.rollback()
        raise http_exc

    except Exception as e:
        # Handle and log general errors (500)
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/tokens/",
            method="POST",
            request_body=token.json(),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response["generalResponse"])
    
    
    
    



@router.delete("/tokens/{token_id}/consumidor/{user_id}")
def delete_token(user_id: int,token_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    try:


        permiso='borrar informacion'

        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()


        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  # Adjust the endpoint as needed
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response

        db_token = db.query(tokensModel).filter(tokensModel.id == token_id).first()
        if not db_token:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Token con ID {token_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/tokens/{token_id}",
                method="DELETE",
                request_body=None,  # No request body for DELETE
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            return response

        # Delete the Token record
        db.delete(db_token)
        db.commit()

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Token con ID {token_id} eliminado exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="DELETE",
            request_body=None,  # No request body for DELETE
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except Exception as e:
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )

        # Log the error
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="DELETE",
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
        
        


@router.put("/tokens/{token_id}/consumidor/{user_id}")
def update_token(user_id: int,token_id: int, token_data: TokenUpdate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    try:

        permiso='actualizar informacion'

        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()


        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  # Adjust the endpoint as needed
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti,
                usuario_id=user_id 
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response

        db_token = db.query(tokensModel).filter(tokensModel.id == token_id).first()

        if not db_token:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message=f"Token con ID {token_id} no encontrado"
            )

            # Log the request and response
            log_entry = Logs(
                endpoint=f"/api/tokens/{token_id}",
                method="PUT",
                request_body=token_data.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()

            return response

        # Update the token fields
        if token_data.numero_serie is not None:
            encrypted_numero_serie = encrypt_data(token_data.numero_serie)
            db_token.numero_serie = encrypted_numero_serie

        if token_data.estado is not None:
            db_token.estado = token_data.estado

        if token_data.tipo_token is not None:
            db_token.tipo_token = token_data.tipo_token

        if token_data.usuario_id is not None:
            db_token.usuario_id = token_data.usuario_id

        if token_data.serie_token_id is not None:
            db_token.serie_token_id = token_data.serie_token_id

        db.commit()
        db.refresh(db_token)

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="El token se actualizo exitosamente",
            information=db_token.to_dict()
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="PUT",
            request_body=token_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se produjo un error: {str(e)}"
        )

        # Log the error
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="PUT",
            request_body=token_data.json(),
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






@router.get("/tokens/{token_id}/consumidor/{user_id}")
def get_token(user_id: int,token_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    try:
        # Fetch the token from the database
        db_token = db.query(tokensModel).filter(tokensModel.id == token_id).first()

        if not db_token:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"El token con ID {token_id} no se encontro"
            )

            # Log the request and response
            log_entry = Logs(
                endpoint=f"/api/tokens/{token_id}",
                method="GET",
                request_body=None,  # No request body for GET
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()

            return response

        # Decrypt the numero_serie field
        decrypted_numero_serie = decrypt_data(db_token.numero_serie)




        print('Intentando ver el token desencriptado:',decrypted_numero_serie,db_token.numero_serie)

        # Prepare the response with decrypted data
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Token obtenido exitosamente",
            information={
                "id": db_token.id,
                "numero_serie": decrypted_numero_serie,
                "estado": db_token.estado,
                "tipo_token": db_token.tipo_token,
                "usuario_id": db_token.usuario_id,
                "serie_token_id": db_token.serie_token_id
            }
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="GET",
            request_body=None,  # No request body for GET
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except Exception as e:
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presento un error: {str(e)}"
        )

        # Log the error
        log_entry = Logs(
            endpoint=f"/api/tokens/{token_id}",
            method="GET",
            request_body=None,  # No request body for GET
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        return response









@router.get("/tokens/consumidor/{user_id}/tokens-por-gerencia")
def get_tokens_by_gerencia(user_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    
    try:
        permiso = 'Visualizar informacion'
        tienePermisos = has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()

        if not tienePermisos:
            response = create_api_response(
                uti=uti,
                status="No autorizado",
                code=200,
                message=f"El usuario {usuario} no tiene permisos para: {permiso}"
            )
            log_entry = Logs(
                endpoint=f"/api/usuarios/consumidor/{user_id}/tokens-by-gerencia",
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            return response

        # Execute the raw SQL query for summary
        summary_query = text("""
        SELECT COUNT(a.numero_serie) AS conteo_tokens,
               a.estado,
               c.nombre AS gerencia
        FROM tokens a
        INNER JOIN usuarios b ON a.usuario_id = b.id
        LEFT JOIN gerencias c ON c.id = b.gerencia_id
        GROUP BY a.estado, c.nombre
        """)
        summary_result = db.execute(summary_query).fetchall()

        # Convert the summary result to a list of dictionaries
        summary_list = [
            {"conteo_tokens": row[0], "estado": row[1], "gerencia": row[2]}
            for row in summary_result
        ]

        # Execute the raw SQL query for details
        detail_query = text("""
        SELECT a.id,
               a.numero_serie,
               a.estado,
               a.tipo_token,
               b.usuario AS usuario_asignado,
               c.nombre AS gerencia,
	           a.serie_token_id                
        FROM tokens a
        INNER JOIN usuarios b ON a.usuario_id = b.id
        LEFT JOIN gerencias c ON c.id = b.gerencia_id
        """)
        detail_result = db.execute(detail_query).fetchall()

        # Convert the detail result to a list of dictionaries
        detail_list = [
            {
                "id": row[0],
                "numero_serie": row[1],
                "estado": row[2],
                "tipo_token": row[3],
                "usuario_asignado": row[4],
                "gerencia": row[5],
                "serie_token": row[6]              
            }
            for row in detail_result
        ]

        # Create the final response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Tokens por gerencia obtenidos exitosamente",
            information={"resumen": summary_list, "detalle": detail_list}
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/usuarios/consumidor/{user_id}/tokens-by-gerencia",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()
        
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
            endpoint=f"/api/usuarios/consumidor/{user_id}/tokens-by-gerencia",
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
