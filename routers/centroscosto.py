from fastapi import FastAPI,Depends,APIRouter, HTTPException, Request, status
from db.database import engine,SessionLocal
from models.models import Paises as PaisesModel,Logs, Gerencias as GerenciasModel,CentrosCosto as CentrosCostosModel,Usuarios,has_permission
from utils import create_api_response,hash_nombre,decrypt_data,encrypt_data
from schemas import GerenciasCreate,CentrosCostoCreate
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




@router.get("/centros_costo/consumidor:{user_id}")
def get_centros_costo(user_id:int,db: Session = Depends(get_db)):
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

        
        centros_costo = db.query(CentrosCostosModel).all()
        centros_costo_list = [centro.to_dict() for centro in centros_costo]

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Centros de costo obtenidos exitosamente",
            information=centros_costo_list
        )

        log_entry = Logs(
            endpoint="/api/centros_costo/",
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
            message=f"Error occurred: {str(e)}"
        )
        log_entry = Logs(
            endpoint="/api/centros_costo/",
            method="GET",
            request_body=None,
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti,
            usuario_id=user_id
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response["generalResponse"])




@router.post("/centros_costo/consumidor/{user_id}")
def create_centros_costo(user_id: int,centros_costo: CentrosCostoCreate, db: Session = Depends(get_db)):
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


#        encrypted_nombre = encrypt_data(centros_costo.nombre)   to encript values
        
        db_centros_costo = CentrosCostosModel(
            nombre=centros_costo.nombre,
            description=centros_costo.description,
            id_gerencia=centros_costo.id_gerencia
        )
        db.add(db_centros_costo)
        db.commit()
        db.refresh(db_centros_costo)

        response = create_api_response(
            uti=uti,
            status="success",
            code=201,
            message="Centro de Costo creado exitosamente"
        )

        log_entry = Logs(
            endpoint="/api/centros_costo/",
            method="POST",
            request_body=centros_costo.json(),
            response_body=json.dumps(response),  # Convert to JSON string
            status_code=201,
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
        # Log the error...
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response["generalResponse"]
        )
        
        





@router.get("/centros_costo/{centros_costo_id}/consumidor/{user_id}")
def get_centros_costo(centros_costo_id: int,user_id:int, db: Session = Depends(get_db)):
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


        
        db_centros_costo = db.query(CentrosCostosModel).filter(CentrosCostosModel.id == centros_costo_id).first()
        
        print('Viendo esto: ',db_centros_costo)
        if not db_centros_costo:
            

            
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Centro de Costo con ID {centros_costo_id} no encontrado"
            )
            # Log the error
            log_entry = Logs(
                endpoint=f"/api/centros_costo/{centros_costo_id}",
                method="GET",
                request_body=None,
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
            usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
#            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])
            return response

        print('Antes de')        
        

        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Centro de Costo obtenido exitosamente",
            information={
                "id": db_centros_costo.id,
                "nombre": db_centros_costo.nombre,
                "description": db_centros_costo.description,
                "id_gerencia": db_centros_costo.id_gerencia
            }
        )
        # Log the request and response
        log_entry = Logs(
            endpoint=f"/api/centros_costo/{centros_costo_id}",
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
        # Log the error
        log_entry = Logs(
            endpoint=f"/api/centros_costo/{centros_costo_id}",
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
        
        
        



@router.delete("/centros_costo/centro_costo/{centros_costo_id}/consumidor/{user_id}")
def delete_centros_costo(centros_costo_id: int,user_id: int, db: Session = Depends(get_db)):
    uti = secrets.token_hex(16)
    try:
        
        permiso='eliminar centros de costo'

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


        db_centros_costo = db.query(CentrosCostosModel).filter(CentrosCostosModel.id == centros_costo_id).first()
        
        # Handle the case where the CentroCosto is not found
        if not db_centros_costo:
            response = create_api_response(
                uti=uti,
                status="error",
                code=404,
                message=f"Centro de Costo con ID {centros_costo_id} no encontrado"
            )
            # Log the not found response
            log_entry = Logs(
                endpoint=f"/api/centros_costo/{centros_costo_id}",
                method="DELETE",
                request_body=None,
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti,
                usuario_id=user_id 
            )
            db.add(log_entry)
            db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response["generalResponse"])

        # Delete the record
        db.delete(db_centros_costo)
        db.commit()

        # Prepare success response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message=f"Centro de Costo con ID {centros_costo_id} eliminado exitosamente"
        )
        # Log the successful request and response
        log_entry = Logs(
            endpoint=f"/api/centros_costo/{centros_costo_id}",
            method="DELETE",
            request_body=None,
            response_body=json.dumps(response),
            status_code=200,
            transaction_id=uti,
            usuario_id=user_id 
        )
        db.add(log_entry)
        db.commit()

        return response

    except HTTPException as http_exc:
        # Handle and log HTTP exceptions (e.g., 404)
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=http_exc.status_code,
            message=http_exc.detail
        )
        log_entry = Logs(
            endpoint=f"/api/centros_costo/{centros_costo_id}",
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
        # Handle and log general exceptions (e.g., 500)
        db.rollback()
        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Se presentó el siguiente error: {str(e)}"
        )
        log_entry = Logs(
            endpoint=f"/api/centros_costo/{centros_costo_id}",
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




@router.get("/centros_costo/consumidor/{user_id}/tokens-por-cc")
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
        select  count(a.numero_serie)conteo_tokens,
	            a.estado,
	            d.nombre centro_costo
        from tokens a inner join usuarios b on a.usuario_id=b.id
            left join gerencias c on c.id=b.gerencia_id
            left join centros_costo d on c.id=d.id_gerencia
        group by a.estado,c.nombre
        """)
        summary_result = db.execute(summary_query).fetchall()

        # Convert the summary result to a list of dictionaries
        summary_list = [
            {"conteo_tokens": row[0], "estado": row[1], "gerencia": row[2]}
            for row in summary_result
        ]

        # Execute the raw SQL query for details
        detail_query = text("""
        select a.id,
            a.numero_serie,
            a.estado,
            a.tipo_token,
            b.nombres||' '||b.apellidos as usuario_asignado ,
            d.nombre centro_costo
        from tokens a inner join usuarios b on a.usuario_id=b.id
        left join gerencias c on c.id=b.gerencia_id
        left join centros_costo d on c.id=d.id_gerencia        
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
            }
            for row in detail_result
        ]

        # Create the final response
        response = create_api_response(
            uti=uti,
            status="success",
            code=200,
            message="Tokens por centro de costo obtenidos exitosamente",
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