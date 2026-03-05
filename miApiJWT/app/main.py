#Importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# CONFIGURACIÓN DE JWT
SECRET_KEY = "tu_clave_secreta_muy_segura_aqui_debe_ser_larga"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# INSTANCIA DEL SERVIDOR
app = FastAPI(
    title="Mi API con JWT",
    description="API con autenticación OAuth2 + JWT",
    version="1.0.0"
)

# BASE DE DATOS FICTICIA

usuarios = [
    {"id": 1, "nombre": "Juan", "edad": 21},
    {"id": 2, "nombre": "Isra", "edad": 23},
    {"id": 3, "nombre": "Abdiel", "edad": 21},
    {"id": 4, "nombre": "Jafet", "edad": 24},
    {"id": 5, "nombre": "Roger", "edad": 19},
]

# Usuario de prueba para login
usuarios_auth = {
    "SeleneLira": {
        "username": "SeleneLira",
        "password": "123456",  
    }
}

# MODELOS PYDANTIC

class UsuarioCreate(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Selene Lira")
    edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 - 123")


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


# CONFIGURACIÓN OAUTH2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# FUNCIONES DE JWT

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Genera un JWT con datos especificados y tiempo de expiración"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    """
    Valida el token JWT y retorna el usuario autenticado.
    Esta función se usa como dependencia en los endpoints protegidos.
    """
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credenciales_invalidas
        token_data = TokenData(username=username)
    except JWTError:
        raise credenciales_invalidas
    
    usuario = usuarios_auth.get(token_data.username)
    if usuario is None:
        raise credenciales_invalidas
    
    return usuario


# ENDPOINTS

@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "¡Bienvenido a mi API con JWT!"}


@app.post("/token", response_model=Token, tags=["Autenticación"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login que genera el JWT.
    Usa usuario: SeleneLira, contraseña: 123456
    """
    # Buscar usuario
    usuario = usuarios_auth.get(form_data.username)
    
    # Validar credenciales
    if not usuario or usuario["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token con expiración de 30 minutos
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": usuario["username"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
    }


@app.get("/HolaMundo", tags=["Bienvenida Asincrónica"])
async def hola():
    """Endpoint asincrónico sin protección"""
    await asyncio.sleep(4)
    return {"mensaje": "¡Hola mundo FastAPI!", "estatus": "200"}


@app.get("/v1/parametroOp/{id}", tags=["Parámetro Obligatorio"])
async def consultaUno(id: int):
    """Endpoint sin protección"""
    return {"Se encontro usuario": id}


@app.get("/v1/parametroOp/", tags=["Parámetro Opcional"])
async def consultaTodos(id: Optional[int] = None):
    """Endpoint sin protección"""
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"mensaje": "usuario encontrado", "usuario": usuario}
        return {"mensaje": "usuario no encontrado", "usuario": id}
    else:
        return {"mensaje": "No se proporcionó id"}


@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def leer_usuarios():
    """Endpoint de lectura sin protección"""
    return {
        "status": "200",
        "total": len(usuarios),
        "usuarios": usuarios
    }


@app.post("/v1/usuarios/", tags=["CRUD HTTP"], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioCreate):
    """Endpoint de creación sin protección"""
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    usuarios.append(usuario.dict())
    return {
        "mensaje": "Usuario agregado",
        "usuario": usuario
    }


@app.put("/v1/usuarios/{id_buscado}", tags=["CRUD HTTP"])
async def actualizar_usuario(
    id_buscado: int,
    datos_nuevos: dict,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Endpoint de actualización PROTEGIDO con JWT.
    Requiere token válido.
    """
    for usr in usuarios:
        if usr["id"] == id_buscado:
            usr.update(datos_nuevos)
            return {
                "mensaje": f"Usuario actualizado por: {usuario_actual['username']}",
                "usuario": usr
            }
    
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )
    


@app.delete("/v1/usuarios/{id}", tags=["CRUD HTTP"], status_code=status.HTTP_200_OK)
async def eliminar_usuario(
    id: int,
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Endpoint de eliminación PROTEGIDO con JWT.
    Requiere token válido.
    """
    for index, usuario in enumerate(usuarios):
        if usuario["id"] == id:
            usuarios.pop(index)
            return {
                "mensaje": f"Usuario eliminado por: {usuario_actual['username']}",
                "id": id
            }
    
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )