# models.py
from sqlalchemy import Column, Integer, String, DateTime,Boolean,ForeignKey,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import bcrypt
from utils import hash_nombre,decrypt_data,create_api_response
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import json
import secrets
import logging
from fastapi.responses import JSONResponse


Base = declarative_base()  # Create the Base class




def has_permission(permission_name: str, user_id: int, db: Session) -> bool:
    uti = secrets.token_hex(16)

    try:

        print('Viendo el permiso y usuario',permission_name,user_id)
        permission_obj = db.query(Permission).filter(Permission.name == permission_name).first()
        role_id = db.query(Usuarios.role_id).filter(Usuarios.id == user_id).scalar()

        print('Este es el permiso',permission_obj)


        if permission_obj is None:
            response = create_api_response(
                uti=uti,
                status="error",
                code=400,
                message=f"Permiso '{permission_name}' no encontrado"
            )
            log_entry = Logs(
                endpoint="/api/permission_check/",  # Adjust the endpoint as needed
                method="POST",
                request_body=json.dumps({"permission_name": permission_name, "user_id": user_id}),
                response_body=json.dumps(response),
                status_code=404,
                transaction_id=uti
            )
            db.add(log_entry)
            db.commit()
            
            error='No se encontro el permiso'
            
            return False




        role_permissions = db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_obj.id
        ).all()


        print('Viendo si encontro el rol:',role_permissions)


        if len(role_permissions) > 0:
            return True
        else:

            return False 
  
    except Exception as e:

        print('Entro a la exepcion del has permission...',e)        
        logging.error("Tratando de ver la excepcion: %s", e)


        response = create_api_response(
            uti=uti,
            status="error",
            code=500,
            message=f"Error in has_permission: {str(e)}"
        )
        
        log_entry = Logs(
            endpoint="/api/permission_check/",  # Adjust the endpoint as needed
            method="POST",
            request_body=json.dumps({"permission_name": permission_name, "user_id": user_id}),
            response_body=json.dumps(response),
            status_code=500,
            transaction_id=uti
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.dumps(response))


class Paises(Base):
    __tablename__ = 'paises'
    id = Column(Integer, primary_key=True, index=True)    
    nombre = Column(String(100), index=True, nullable=False) 
    codigo = Column(String(100), index=True, nullable=False)     
    codigo_postal = Column(String(100), index=True, nullable=False) 

#    usuarios = relationship('Usuarios', back_populates='pais')
    usuarios = relationship('Usuarios', back_populates='pais')


    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "codigo_postal": self.codigo_postal
        }
        



class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    transaction_id= Column(String(200), nullable=True)
    usuario_id=Column(Integer,nullable=True)    
    
    

class CentrosCosto(Base):
    __tablename__ = 'centros_costo'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=True)
    description = Column(String(255), nullable=True)


    id_gerencia = Column(Integer, ForeignKey('gerencias.id',ondelete='SET NULL'), nullable=True)
    gerencia = relationship("Gerencias", back_populates="centros_costo")




    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "description": self.description,
            "id_gerencia": self.id_gerencia,
            "gerencia": self.gerencia.nombre if self.gerencia else None
        }




class Gerencias(Base):
    __tablename__ = 'gerencias'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)

    centros_costo = relationship("CentrosCosto", back_populates="gerencia")
    usuarios = relationship('Usuarios', back_populates='gerencia')
    

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre
        }


class Usuarios(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(100), unique=True, nullable=False) 
    password = Column(String(100), nullable=False)     
    nombres = Column(String(100), nullable=False) 
    apellidos = Column(String(100), nullable=False) 
    telefono = Column(String(100), nullable=False)
    

    gerencia_id = Column(Integer, ForeignKey('gerencias.id',ondelete='SET NULL'), nullable=True)
    gerencia = relationship('Gerencias', back_populates='usuarios')

    pais_id = Column(Integer, ForeignKey('paises.id', ondelete='SET NULL'), nullable=True)
    pais = relationship('Paises', back_populates='usuarios')
    
    tokens = relationship("Tokens", back_populates="usuario")  # Relationship with Tokens

    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    role = relationship("Roles", back_populates="usuarios")



    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "telefono": self.telefono,
            "pais_id": self.pais_id,
            "pais": self.pais.to_dict() if self.pais else None,
            "gerencia_id": self.gerencia_id,
            "gerencia": self.gerencia.to_dict() if self.gerencia else None,  
            "role_id": self.role_id,
            "role": self.role.to_dict() if self.role else None,                        
        }
        


  
  
  
  
class Tokens(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String(100), index=True, nullable=False)
    estado = Column(Boolean, default=True)
    tipo_token = Column(String(50), nullable=False)

    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)  # Foreign key to Usuarios
    usuario = relationship("Usuarios", back_populates="tokens")  # Relationship with Usuarios

    serie_token_id = Column(Integer, ForeignKey('series_token.id'), nullable=True)  # Foreign key to SeriesToken
    serie_token = relationship("SeriesToken", back_populates="tokens")  # Relationship with SeriesToken


    
    def to_dict(self):
        return {
            "id": self.id,
            "numero_serie": self.numero_serie,#decrypt_data(self.numero_serie) if self.numero_serie else None,
            "estado": self.estado,
            "tipo_token": self.tipo_token,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.to_dict() if self.usuario else None,
            "serie_token_id": self.serie_token_id,
            "serie_token": self.serie_token.to_dict() if self.serie_token else None,
        }    
    
    
    
    
class SeriesToken(Base):
    __tablename__ = 'series_token'

    id = Column(Integer, primary_key=True, index=True)    
    nombre_serie = Column(String(100), index=True, nullable=False) 
    fecha_expiracion = Column(DateTime(timezone=True), server_default=func.now())
      
    tokens = relationship("Tokens", back_populates="serie_token")  # Relationship with Tokens

  
class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    usuarios = relationship("Usuarios", back_populates="role")
    


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
        

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
        

class RolePermission(Base):
    __tablename__ = 'role_permissions'

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)


    def to_dict(self):
        return {
            "role_id": self.role_id,
            "permission_id": self.permission_id
        }
        



