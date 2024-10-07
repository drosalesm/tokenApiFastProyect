from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Usuarios as usuariosModels,Logs,Paises, Gerencias as GerenciasModel,has_permission,Roles
from utils import create_api_response,hash_password,verify_password
from schemas import UsuariosCreate
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


@router.get("/usuarios/consumidor/{user_id}")
def get_all_usuarios(user_id: int,db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    
    try:


        permiso='Visualizar informacion'
        tienePermisos=has_permission(permiso, user_id, db)
        usuario = db.query(usuariosModels.usuario).filter(usuariosModels.id == user_id).scalar()



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


        usuarios = db.query(usuariosModels).all()
        
        # Convert the list of users to dictionaries
        usuarios_list = [usuario.to_dict() for usuario in usuarios]
        
        # Log the request and response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Usuarios obtenidos exitosamente",
            information=usuarios_list
        )

        log_entry = Logs(
            endpoint="/api/usuarios/",
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
            message=f"Se presento el siguiente error: {str(e)}"
        )
        
        log_entry = Logs(
            endpoint="/api/usuarios/",
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
        


@router.post("/usuarios/consumidor/{user_id}", response_model=dict)
def create_usuario(user_id: int, usuario: UsuariosCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:
        permiso = 'crear usuario'
        tienePermisos = has_permission(permiso, user_id, db)
        usuario_nombre = db.query(usuariosModels.usuario).filter(usuariosModels.id == user_id).scalar()

#        if not tienePermisos:
#            response = create_api_response(
#                uti=uti,
#                status="No autorizado",
#                code=200,
#                message=f"El usuario {usuario_nombre} no tiene permisos para: {permiso}"
#            )
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

        # Check if the usuario with the same username already exists
        existing_usuario = db.query(usuariosModels).filter(usuariosModels.usuario == usuario.usuario).first()
        if existing_usuario:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message=f"El usuario con nombre '{usuario.usuario}' ya existe."
            )
            return response

        # Check if the related pais exists if provided
        if usuario.pais_id:
            pais = db.query(Paises).filter(Paises.id == usuario.pais_id).first()
            if not pais:
                response = create_api_response(
                    uti=uti,
                    status="error",
                    code=404,
                    message=f"País con ID {usuario.pais_id} no encontrado"
                )
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Check if the related gerencia exists if provided
        if usuario.gerencia_id:
            gerencia = db.query(GerenciasModel).filter(GerenciasModel.id == usuario.gerencia_id).first()
            if not gerencia:
                response = create_api_response(
                    uti=uti,
                    status="error",
                    code=404,
                    message=f"Gerencia con ID {usuario.gerencia_id} no encontrado"
                )
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Check if the related role exists if provided
        if usuario.role_id:
            role = db.query(Roles).filter(Roles.id == usuario.role_id).first()
            if not role:
                response = create_api_response(
                    uti=uti,
                    status="error",
                    code=404,
                    message=f"Rol con ID {usuario.role_id} no encontrado"
                )
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Hash the password before storing
        hashed_password = hash_password(usuario.password)

        # Create and add the new usuario to the database
        db_usuario = usuariosModels(
            usuario=usuario.usuario,
            password=hashed_password,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            telefono=usuario.telefono,
            pais_id=usuario.pais_id,
            gerencia_id=usuario.gerencia_id,
            role_id=usuario.role_id
        )
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message="Usuario creado exitosamente",
            information={"id": db_usuario.id}
        )

        # Log the request and response
        log_entry = Logs(
            endpoint="/api/usuarios/",
            method="POST",
            request_body=usuario.json(),
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
            endpoint="/api/usuarios/",
            method="POST",
            request_body=usuario.json(),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response["generalResponse"])





@router.delete("/usuarios/{usuario_id}/consumidor/{user_id}")
def delete_usuario(user_id: int,usuario_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    
    try:
   
   
        permiso = 'borrar usuario'
        tienePermisos = has_permission(permiso, user_id, db)
        usuario_nombre = db.query(usuariosModels.usuario).filter(usuariosModels.id == user_id).scalar()

        if not tienePermisos:
            response = create_api_response(
                uti=uti,
                status="No autorizado",
                code=200,
                message=f"El usuario {usuario_nombre} no tiene permisos para: {permiso}"
            )
            log_entry = Logs(
                endpoint="/api/permission_check/",
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
   
   
        # Retrieve the user from the database
        db_usuario = db.query(usuariosModels).filter(usuariosModels.id == usuario_id).first()
        
        if not db_usuario:
            # User not found, log and return 404 Not Found response
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Usuario con ID {usuario_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/usuarios/{usuario_id}",
                method="DELETE",
                request_body=None,  # No request body for DELETE
                response_body=json.dumps(response),  # Convert to JSON string
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Delete the user
        db.delete(db_usuario)
        db.commit()

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Usuario con ID {usuario_id} eliminado exitosamente"
        )

        # Log the successful deletion
        log_entry = Logs(
            endpoint=f"/api/usuarios/{usuario_id}",
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
        # Rollback transaction and log HTTP errors (404)
        db.rollback()
        # Ensure the log is only created for HTTP exceptions
        response = create_api_response(
            uti=uti,
            status="error",
            code=http_exc.status_code,
            message=http_exc.detail
        )
        log_entry = Logs(
            endpoint=f"/api/usuarios/{usuario_id}",
            method="DELETE",
            request_body=None,
            response_body=json.dumps(response),
            status_code=http_exc.status_code,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        raise http_exc

    except Exception as e:
        # Rollback transaction and handle unexpected errors (500)
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        # Log the error
        log_entry = Logs(
            endpoint=f"/api/usuarios/{usuario_id}",
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
    





@router.put("/usuarios/{usuario_id}")
def update_usuario(usuario_id: int, usuario_data: UsuariosCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:
        # Fetch the existing Usuarios record from the database
        db_usuario = db.query(usuariosModels).filter(usuariosModels.id == usuario_id).first()
        if not db_usuario:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Usuario con ID {usuario_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/usuarios/{usuario_id}",
                method="PUT",
                request_body=usuario_data.json(),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
                usuario_id=usuario_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Update the Usuarios record with the new data
        if usuario_data.usuario is not None:
            db_usuario.usuario = usuario_data.usuario
        if usuario_data.password is not None:
            db_usuario.password = hash_password(usuario_data.password)
        if usuario_data.nombres is not None:
            db_usuario.nombres = usuario_data.nombres
        if usuario_data.apellidos is not None:
            db_usuario.apellidos = usuario_data.apellidos
        if usuario_data.telefono is not None:
            db_usuario.telefono = usuario_data.telefono
        if usuario_data.gerencia_id is not None:
            db_usuario.gerencia_id = usuario_data.gerencia_id
        if usuario_data.pais_id is not None:
            db_usuario.pais_id = usuario_data.pais_id
        if usuario_data.role_id is not None:
            db_usuario.role_id = usuario_data.role_id


        db.commit()
        db.refresh(db_usuario)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Usuario actualizado exitosamente",
            information=db_usuario.to_dict()
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/usuarios/{usuario_id}",
            method="PUT",
            request_body=usuario_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=usuario_id
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
            endpoint=f"/api/usuarios/{usuario_id}",
            method="PUT",
            request_body=usuario_data.json(),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti,
            usuario_id=usuario_id
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )