from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs,has_permission,Usuarios
from utils import create_api_response
from schemas import PaisesCreate
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

@router.post("/paises/consumidor/{user_id}")


def create_pais(user_id: int,pais: PaisesCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:
        # Validate input fields
        if not pais.nombre:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo nombre de pais no puede estar vacio"
            )
            log_entry = Logs(
                endpoint="/api/paises/",
                method="POST",
                request_body=pais.json(),
                response_body=json.dumps(response),  # Convert to JSON string
                status_code=400,
                transaction_id=uti,
                usuario_id=user_id  
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])
        
        if not pais.codigo:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo Codigo de pais no puede estar vacio"
            )
            log_entry = Logs(
                endpoint="/api/paises/",
                method="POST",
                request_body=pais.json(),
                response_body=json.dumps(response),  
                status_code=400,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])

        if not pais.codigo_postal:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message="El campo Codigo postal no puede estar vacio"
            )
            log_entry = Logs(
                endpoint="/api/paises/",
                method="POST",
                request_body=pais.json(),
                response_body=json.dumps(response),  
                status_code=400,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["generalResponse"])


        db_pais = PaisesModel(**pais.dict())
        db.add(db_pais)
        db.commit()
        db.refresh(db_pais)

        # Log the request and response for successful creation
        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message=f"Pais '{pais.nombre}' creado exitosamente"
        )
        log_entry = Logs(
            endpoint="/api/paises/",
            method="POST",
            request_body=pais.json(),
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
            message=f"Se presento el siguiente error: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/paises/",
            method="POST",
            request_body=pais.json(),
            response_body=json.dumps(response),  
            status_code=500,
            transaction_id=uti,
                usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response




@router.get("/paises/consumidor/{user_id}")
def get_all_paises(user_id: int, db: Session = Depends(get_db)):
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

        
        paises = db.query(PaisesModel).all()
        
        paises_list = [pais.to_dict() for pais in paises]
        
        # Log the request and response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Paises obtenidos exitosamente",
            information=paises_list
        )

        log_entry = Logs(
            endpoint="/api/paises/",
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
            endpoint="/api/paises/",
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





@router.delete("/paises/{pais_id}/consumer/{user_id}")
def delete_pais(user_id: int, pais_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    try:
        permiso = 'borrar informacion'

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
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            return response

        db_pais = db.query(PaisesModel).filter(PaisesModel.id == pais_id).first()

        if not db_pais:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Pais con ID {pais_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/paises/{pais_id}",
                method="DELETE",
                request_body=None,  # No request body for DELETE
                response_body=json.dumps(response),
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

        db.delete(db_pais)
        db.commit()

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Pais con ID {pais_id} eliminado exitosamente"
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/paises/{pais_id}",
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
            endpoint=f"/api/paises/{pais_id}",
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

    
    
    
    


@router.put("/paises/{pais_id}/consumidor/{user_id}")
def update_pais(user_id:int,pais_id: int, pais_data: PaisesCreate, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)

    try:


        permiso = 'actualizar informacion'

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
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            return response


        db_pais = db.query(PaisesModel).filter(PaisesModel.id == pais_id).first()
        
        if not db_pais:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Pais con ID {pais_id} no encontrado"
            )
            log_entry = Logs(
                endpoint=f"/api/paises/{pais_id}",
                method="PUT",
                request_body=pais_data.json(),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Update the Paises record with the new data
        if pais_data.nombre is not None:
            db_pais.nombre = pais_data.nombre
        if pais_data.codigo is not None:
            db_pais.codigo = pais_data.codigo
        if pais_data.codigo_postal is not None:
            db_pais.codigo_postal = pais_data.codigo_postal

        db.commit()
        db.refresh(db_pais)

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Pais actualizado exitosamente",
            information=db_pais.to_dict()
        )

        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/paises/{pais_id}",
            method="PUT",
            request_body=pais_data.json(),
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
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
            endpoint=f"/api/paises/{pais_id}",
            method="PUT",
            request_body=pais_data.json(),
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









