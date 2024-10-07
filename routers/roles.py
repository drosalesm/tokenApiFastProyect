from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Logs,Roles as RolesModel,has_permission,Usuarios
from utils import create_api_response,hash_password,verify_password
from schemas import UsuariosCreate,RolesCreate
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





@router.get("/roles/consumidor/{user_id}")
def get_all_roles(user_id: int,db: Session = Depends(get_db)):
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



        roles = db.query(RolesModel).all()
        
        # Convert the list of roles to dictionaries
        roles_list = [role.to_dict() for role in roles]
        
        # Log the request and response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Roles obtenidos exitosamente",
            information=roles_list
        )

        log_entry = Logs(
            endpoint="/api/roles/",
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
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        
        log_entry = Logs(
            endpoint="/api/roles/",
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







@router.post("/roles/consumidor/{user_id}")
def create_role(user_id: int,role: RolesCreate, db: Session = Depends(get_db)):
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



        if not role.name:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo nombre del rol no puede estar vacío"
            )
            log_entry = Logs(
                endpoint="/api/roles/",
                method="POST",
                request_body=role.json(),
                response_body=json.dumps(response),  # Convert to JSON string
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        # Create the new role in the database
        db_role = RolesModel(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)

        # Log the request and response for successful creation
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message=f"Rol '{role.name}' creado exitosamente"
        )
        log_entry = Logs(
            endpoint="/api/roles/",
            method="POST",
            request_body=role.json(),
            response_body=json.dumps(response),  # Convert to JSON string
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
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/roles/",
            method="POST",
            request_body=role.json(),
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








@router.put("/roles/{role_id}/consumidor/{user_id}")
def update_role(user_id: int,role_id: int, role_data: RolesCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:


        permiso='actualizar roles'
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


        db_role = db.query(RolesModel).filter(RolesModel.id == role_id).first()
        if not db_role:
            # Role not found, return a 404 response
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Rol con ID {role_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/roles/{role_id}",
                method="PUT",
                request_body=role_data.json(),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Update the Roles record with the new data
        if role_data.name is not None:
            db_role.name = role_data.name
        if role_data.description is not None:
            db_role.description = role_data.description

        db.commit()
        db.refresh(db_role)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Rol actualizado exitosamente",
            information=db_role.to_dict()
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/roles/{role_id}",
            method="PUT",
            request_body=role_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle HTTP exceptions separately
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
            endpoint=f"/api/roles/{role_id}",
            method="PUT",
            request_body=role_data.json(),
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








@router.delete("/roles/{role_id}/consumidor/{user_id}")
def delete_role(user_id: int,role_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:


        permiso='eliminar roles'
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


        db_role = db.query(RolesModel).filter(RolesModel.id == role_id).first()
        
        if not db_role:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Rol con ID {role_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/roles/{role_id}",
                method="DELETE",
                request_body=None,
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Delete the Role record
        db.delete(db_role)
        db.commit()

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Rol con ID {role_id} eliminado exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/roles/{role_id}",
            method="DELETE",
            request_body=None,
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
            endpoint=f"/api/roles/{role_id}",
            method="DELETE",
            request_body=None,
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
