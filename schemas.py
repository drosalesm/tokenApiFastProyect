from pydantic import BaseModel
from typing import Optional,List


class PaisesBase(BaseModel):
    nombre: str
    codigo: str
    codigo_postal: str



# Pydantic Schema for Request
class PaisesCreate(BaseModel):
    nombre: str
    codigo: str
    codigo_postal: str

# Pydantic Schema for Response
class PaisesResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    codigo_postal: str

    class Config:
        orm_mode = True
        

class UsuariosCreate(BaseModel):
    usuario: str
    password: Optional[str] = None    
    nombres: str
    apellidos: str
    telefono: str
    pais_id: Optional[int] = None  # Optional field for country reference
    gerencia_id: Optional[int] = None
    role_id:Optional[int] = None

    class Config:
        orm_mode = True
    

class UsuariosResponse(BaseModel):
    id: int
    usuario: str
    nombres: str
    apellidos: str
    telefono: str

    class Config:
        orm_mode = True
        

class GerenciasCreate(BaseModel):
    nombre: str


class CentrosCostoCreate(BaseModel):
    nombre: Optional[str] = None
    description: Optional[str] = None
    id_gerencia: Optional[int] = None



class TokensCreate(BaseModel):
    numero_serie: str
    estado: bool
    tipo_token: str
    usuario_id: Optional[int] = None  # Optional field for user ID
    serie_token_id: Optional[int] = None  # Optional field for series token ID
    


class TokenUpdate(BaseModel):
    numero_serie: Optional[str] = None
    estado: Optional[bool] = None
    tipo_token: Optional[str] = None
    usuario_id: Optional[int] = None
    serie_token_id: Optional[int] = None
    
    
class RolesCreate(BaseModel):
    name: str
    description: Optional[str] = None
    

class PermissionCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True
        
class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int
    
    
class LoginRequest(BaseModel):
    usuario: str
    password: str
    
    
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    
    

# Pydantic models
class LogEntry(BaseModel):
    endpoint: str
    method: str
    request_body: dict
    response_body: dict
    codigo_trans: int
    fecha_trans: str
    usuario: str
    
class LogResponse(BaseModel):
    logs: List[LogEntry]