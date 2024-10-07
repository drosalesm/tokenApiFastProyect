from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status,Query
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs, Permission as PermissionsModel,Roles,RolePermission,has_permission,Usuarios
from utils import create_api_response
from schemas import RolePermissionCreate
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




@router.post("/role-permissions/")
def create_role_permission(role_permission: RolePermissionCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:
        # Check if the role exists
        db_role = db.query(Roles).filter(Roles.id == role_permission.role_id).first()
        if not db_role:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El rol con el ID proporcionado no existe"
            )
            log_entry = Logs(
                endpoint="/api/role-permissions/",
                method="POST",
                request_body=role_permission.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        # Check if the permission exists
        db_permission = db.query(PermissionsModel).filter(PermissionsModel.id == role_permission.permission_id).first()
        if not db_permission:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El permiso con el ID proporcionado no existe"
            )
            log_entry = Logs(
                endpoint="/api/role-permissions/",
                method="POST",
                request_body=role_permission.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        # Check if the role-permission relationship already exists
        existing_relation = db.query(RolePermission).filter(
            RolePermission.role_id == role_permission.role_id,
            RolePermission.permission_id == role_permission.permission_id
        ).first()
        
        if existing_relation:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="La relación de rol y permiso ya existe"
            )
            log_entry = Logs(
                endpoint="/api/role-permissions/",
                method="POST",
                request_body=role_permission.json(),
                response_body=json.dumps(response),
                status_code=400,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        # Create new RolePermission record
        db_role_permission = RolePermission(
            role_id=role_permission.role_id,
            permission_id=role_permission.permission_id
        )
        db.add(db_role_permission)
        db.commit()
        db.refresh(db_role_permission)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message="Relación de rol y permiso creada exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint="/api/role-permissions/",
            method="POST",
            request_body=role_permission.json(),
            response_body=json.dumps(response),
            status_code=201,
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
            endpoint="/api/role-permissions/",
            method="POST",
            request_body=role_permission.json(),
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



@router.get("/role-permissions/consumidor:{user_id}")
def get_all_role_permissions(user_id: int, db: Session = Depends(get_db)):
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

        # Join RolePermission with Roles and Permissions
        role_permissions = db.query(
            RolePermission,
            Roles.name.label('role_name'),
            PermissionsModel.description.label('permission_description')
        ).join(Roles, RolePermission.role_id == Roles.id) \
         .join(PermissionsModel, RolePermission.permission_id == PermissionsModel.id) \
         .all()

        # Convert the list of associations to dictionaries
        role_permissions_list = [
            {
                "role_id": rp.RolePermission.role_id,
                "role_name": rp.role_name,
                "permission_id": rp.RolePermission.permission_id,
                "permission_description": rp.permission_description
            }
            for rp in role_permissions
        ]

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Permisos y roles obtenidos exitosamente",
            information=role_permissions_list
        )

        # Log the request and response
        log_entry = Logs(
            endpoint="/api/role-permissions/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti
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
            message=f"An error occurred: {str(e)}"
        )

        # Log the error
        log_entry = Logs(
            endpoint="/api/role-permissions/",
            method="GET",
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







@router.delete("/role-permissions/")
def delete_role_permission(
    role_id: int = Query(..., description="ID of the role to delete"),
    permission_id: int = Query(..., description="ID of the permission to delete"),
    db: Session = Depends(get_db)
):
    uti = secrets.token_hex(16)

    try:





        db_role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()

        if not db_role_permission:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Relación de rol-permiso con rol ID {role_id} y permiso ID {permission_id} no encontrada"
            )
            log_entry = Logs(
                endpoint=f"/api/role-permissions/",
                method="DELETE",
                request_body=None,
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Delete the RolePermission record
        db.delete(db_role_permission)
        db.commit()

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Relación de rol-permiso con rol ID {role_id} y permiso ID {permission_id} eliminada exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/role-permissions/",
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
            endpoint=f"/api/role-permissions/",
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