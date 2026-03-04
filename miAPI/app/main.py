#Importaciones
from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel,Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

#instancia del servidor 
app = FastAPI(
    title="Mi primer API",
    description="Jafet uribe uribe",
    version="1.0.0"
    )
#BD ficticia
usuarios=[
    {"id": 1, "nombre":"Juan", "edad" :21 },
    {"id": 2, "nombre":"Isra", "edad" :23 },
    {"id": 3, "nombre":"Abdiel", "edad" :21 },
    {"id": 4, "nombre":"Jafet", "edad" :24 },
    {"id": 5, "nombre":"Roger", "edad" :19 },
]

#modelo de validacion pydantic
class usuario_create(BaseModel):
    id: int = Field(...,gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Selene Lira")
    edad: int = Field(..., ge=1, le=123, description="Edad valida entre 1 - 123")


#seguridad

security = HTTPBasic()
def verificar_Peticion(credenciales:HTTPBasicCredentials=Depends(security)):
    userAuth = secrets.compare_digest(credenciales.username,"SeleneLira")
    passAuth = secrets.compare_digest(credenciales.password,"123456")

    if not(userAuth and passAuth):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= " Credenciales no Autorizadas"
        )
    
    return credenciales.username





#endpoints
@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje" : "¡Bienvenido a mi API!"}

@app.get("/HolaMundo" ,tags=["Bienvenida Asincrona"])
async def hola():
    await asyncio.sleep(4)
    return {"mensaje" : "¡Hola mundo FastAPI! ",
            "estatus": "200"
            }

@app.get("/v1/parametroOp/{id}", tags=["Parametro obligatorio"])
async def consultaUno(id:int):
    return {"Se encontro usuario" : id}


@app.get("/v1/parametroOp/", tags=["Parametro opcional"])
async def consultaTodos(id:Optional[int]=None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return{"mensaje:":"usuario encontrado", "usuario":usuario}
        return{"mensaje:":"usuario no encontrado", "usuario":id}
    else:
        return{"mensaje:":"No se proporciono id"}
    

@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def leer_usuarios():
    return{
        "status":"200",
        "total": len(usuarios),
        "usuarios":usuarios
    }

@app.post("/v1/usuarios/",tags=["CRUD HTTP"],status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:usuario_create):
    for usr in usuarios:
        if usr ["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario agregado",
        "Usuario":usuario
    }

@app.put("/v1/usuarios/{id_buscado}", tags=["CRUD HTTP"])
async def actualizar_usuario(id_buscado: int, datos_nuevos: dict):
    for usr in usuarios:
        if usr["id"] == id_buscado:
            usr.update(datos_nuevos)
            return {
                "mensaje": "Usuario actualizado",
                "usuario": usr
            }
        
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )  

@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'], status_code=status.HTTP_200_OK)
async def eliminar_usuario(id:int, userAuth:str= Depends(verificar_Peticion)):
    for usuario in usuarios:
        if usuario["id"] == id:
            usuarios.pop(index)
            return{
                "messege":f"Usuario eliminado por: {userAuth}"
            }
    raise HTTPException(
        status_code=400, 
        detail="Usuario no encontrado"
    )