from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs, Permission as PermisionsModel,Usuarios,has_permission
from utils import create_api_response
from schemas import PermissionCreate
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



@router.get("/permissions/consumidor:{user_id}")
def get_all_permissions(user_id: int, db: Session = Depends(get_db)):
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
                transaction_id=uti
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response



        permissions = db.query(PermisionsModel).all()
        
        # Convert the list of permissions to dictionaries
        permissions_list = [permission.to_dict() for permission in permissions]
        
        # Log the request and response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Permisos obtenidos exitosamente",
            information=permissions_list
        )

        log_entry = Logs(
            endpoint="/api/permissions/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=200,
            transaction_id=uti
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
            message=f"Se produjo un error: {str(e)}"
        )
        
        log_entry = Logs(
            endpoint="/api/permissions/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )
        
        


@router.post("/permissions/consumidor/{user_id}")
def create_permission(user_id: int,permission: PermissionCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:

        permiso='crear informacion'
        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()

#        if not tienePermisos:                               

#            response = create_api_response(
#                    uti=uti,
#                    status="No autorizado",
#                    code=200,
#                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
#            log_entry = Logs(
#                endpoint="/api/permission_check/",  
#                method="GET",
#                request_body=None,
#                response_body=json.dumps(response),
#                status_code=200,
#                transaction_id=uti
#            )
                        
#            db.add(log_entry)
#            db.commit()
                
#            return response


        if not permission.name:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo permisos no puede ir vacio."
            )
            log_entry = Logs(
                endpoint="/api/permissions/",
                method="POST",
                request_body=permission.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        if not permission.description:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo descripcion no puede ser vacio."
            )
            log_entry = Logs(
                endpoint="/api/permissions/",
                method="POST",
                request_body=permission.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        # Create a new Permission instance and add it to the database
        db_permission = PermisionsModel(**permission.dict())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)

        # Log the request and response for successful creation
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message=f"Permiso '{permission.name}' creado exitosamente."
        )
        log_entry = Logs(
            endpoint="/api/permissions/",
            method="POST",
            request_body=permission.json(),
            response_body=json.dumps(response),
            status_code=201,
            transaction_id=uti
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
            message=f"An error occurred: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/permissions/",
            method="POST",
            request_body=permission.json(),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        return response
    
    





@router.put("/permissions/{permission_id}/consumidor/{user_id}")
def update_permission(user_id: int,permission_id: int, permission_data: PermissionCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:


        permiso='actualizar permisos'
        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()

        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response


        db_permission = db.query(PermisionsModel).filter(PermisionsModel.id == permission_id).first()
        
        if not db_permission:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Permiso con ID {permission_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/permissions/{permission_id}",
                method="PUT",
                request_body=permission_data.json(),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Actualizar el registro de Permiso con los nuevos datos
        if permission_data.name is not None:
            db_permission.name = permission_data.name
        if permission_data.description is not None:
            db_permission.description = permission_data.description

        db.commit()
        db.refresh(db_permission)

        # Preparar respuesta de éxito
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Permiso actualizado exitosamente",
            information=db_permission.to_dict()
        )

        # Registrar la solicitud y respuesta
        log_entry = Logs(
            endpoint=f"/api/permissions/{permission_id}",
            method="PUT",
            request_body=permission_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Manejar y registrar errores HTTP (por ejemplo, 404 No encontrado)
        db.rollback()
        raise http_exc

    except Exception as e:
        # Manejar y registrar errores generales (500)
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )

        # Registrar el error
        log_entry = Logs(
            endpoint=f"/api/permissions/{permission_id}",
            method="PUT",
            request_body=permission_data.json(),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )










@router.delete("/permissions/{permission_id}/consumidor/{user_id}")
def delete_permission(user_id: int,permission_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:

        permiso='borrar permisos'
        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(Usuarios.usuario).filter(Usuarios.id == user_id).scalar()

        if not tienePermisos:                               

            response = create_api_response(
                    uti=uti,
                    status="No autorizado",
                    code=200,
                    message=f"El usuario {usuario} no tiene permisos para:{permiso}")
            log_entry = Logs(
                endpoint="/api/permission_check/",  
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=200,
                transaction_id=uti
            )
                        
            db.add(log_entry)
            db.commit()
                
            return response


        db_permission = db.query(PermisionsModel).filter(PermisionsModel.id == permission_id).first()

        if not db_permission:
            # Permission not found, return a 404 response
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Permiso con ID {permission_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/permissions/{permission_id}",
                method="DELETE",
                request_body=None,  # No request body for DELETE
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Delete the Permission record
        db.delete(db_permission)
        db.commit()

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Permiso con ID {permission_id} eliminado exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/permissions/{permission_id}",
            method="DELETE",
            request_body=None,  # No request body for DELETE
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle and log HTTP errors (e.g., 404 Not Found)
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
            endpoint=f"/api/permissions/{permission_id}",
            method="DELETE",
            request_body=None,  # No request body for DELETE
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )
