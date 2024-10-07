from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs, Gerencias as GerenciasModel,has_permission,Usuarios
from utils import create_api_response
from schemas import GerenciasCreate
from sqlalchemy.orm import Session
import json
import secrets


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()




@router.get("/gerencias/consumidor/{user_id}")
def get_all_gerencias(user_id: int,db: Session = Depends(get_db)):
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



        gerencias = db.query(GerenciasModel).all()
        
        # Convert the list of Gerencias to dictionaries
        gerencias_list = [gerencia.to_dict() for gerencia in gerencias]
        
        # Log the request and response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Gerencias obtenidas exitosamente",
            information=gerencias_list
        )

        log_entry = Logs(
            endpoint="/api/gerencias/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),  # Convert to JSON string
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
            endpoint="/api/gerencias/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),  # Convert to JSON string
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
        
        
    

@router.post("/gerencias/consumer/{user_id}")
def create_gerencia(user_id: int,gerencia: GerenciasCreate, db: Session = Depends(get_db)):
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

        

        if not gerencia.nombre:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo nombre de la gerencia no puede estar vacío"
            )
            log_entry = Logs(
                endpoint="/api/gerencias/",
                method="POST",
                request_body=gerencia.json(),
                response_body=json.dumps(response),  # Convert to JSON string
                status_code=400,
                transaction_id=uti,
                usuario_id=user_id
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])
        
        # Create a new Gerencia record
        db_gerencia = GerenciasModel(**gerencia.dict())
        db.add(db_gerencia)
        db.commit()
        db.refresh(db_gerencia)

        # Log the request and response for successful creation
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message=f"Gerencia '{gerencia.nombre}' creada exitosamente"
        )
        log_entry = Logs(
            endpoint="/api/gerencias/",
            method="POST",
            request_body=gerencia.json(),
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=201,
            transaction_id=uti,
            usuario_id=user_id
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle and log HTTP errors (400)
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
            endpoint="/api/gerencias/",
            method="POST",
            request_body=gerencia.json(),
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=500,
            transaction_id=uti,
            usuario_id=user_id
        )
        db.add(log_entry)
        db.commit()

        return response
    





@router.delete("/gerencias/{gerencia_id}/consumer/{user_id}")
def delete_gerencia(user_id:int,gerencia_id: int, db: Session = Depends(get_db)):
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
                    message=f"El usuario {usuario} no tiene permisos para: {permiso}")
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

        
        db_gerencia = db.query(GerenciasModel).filter(GerenciasModel.id == gerencia_id).first()
        
        if not db_gerencia:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Gerencia con ID {gerencia_id} no encontrada"
            )
            log_entry = Logs(
                endpoint=f"/api/gerencias/{gerencia_id}",
                method="DELETE",
                request_body=None,  # No request body for DELETE
                response_body=json.dumps(response),  # Convert to JSON string
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id
            )
            db.add(log_entry)
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response["generalResponse"]
            )

        db.delete(db_gerencia)
        db.commit()

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Gerencia con ID {gerencia_id} eliminada exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/gerencias/{gerencia_id}",
            method="DELETE",
            request_body=None,  # No request body for DELETE
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=200,
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

        # Log the error
        log_entry = Logs(
            endpoint=f"/api/gerencias/{gerencia_id}",
            method="DELETE",
            request_body=None,
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti,
            usuario_id=user_id
        )
        db.add(log_entry)
        db.commit()

        return response
    
    

@router.put("/gerencias/{gerencia_id}/consumer/{user_id}")
def update_gerencia(user_id:int,gerencia_id: int, gerencia_data: GerenciasCreate, db: Session = Depends(get_db)):
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
                    message=f"El usuario {usuario} no tiene permisos para: {permiso}")
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



        db_gerencia = db.query(GerenciasModel).filter(GerenciasModel.id == gerencia_id).first()

        if not db_gerencia:
            # Handle the 404 error if the Gerencia is not found
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Gerencia con ID {gerencia_id} no encontrada"
            )
            log_entry = Logs(
                endpoint=f"/api/gerencias/{gerencia_id}",
                method="PUT",
                request_body=gerencia_data.json(),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Update the Gerencia record with the new data
        if gerencia_data.nombre is not None:
            db_gerencia.nombre = gerencia_data.nombre

        db.commit()
        db.refresh(db_gerencia)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Gerencia actualizada exitosamente",
            information=db_gerencia.to_dict()
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/gerencias/{gerencia_id}",
            method="PUT",
            request_body=gerencia_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle known HTTP exceptions
        db.rollback()
        raise http_exc

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
            endpoint=f"/api/gerencias/{gerencia_id}",
            method="PUT",
            request_body=gerencia_data.json(),
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
