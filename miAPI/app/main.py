from fastapi import FastAPI, status ,HTTPException 
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
#Instancia del servidor
app = FastAPI(
    title="Mi primer API",
    description="Selene Lira ",
    version="1.0.0"
    )

usuarios=[
    {"id":1,"nombre":"Juan","edad":21},
    {"id":2,"nombre":"Israel","edad":21},
    {"id":3,"nombre":"Sofi","edad":21}
]

#Modelo de validación
class usuario_create(BaseModel):
    id: int = Field(...,gt=0, description="Identificador de usuario")
    nombre: str = Field(...,min_length=3,max_length=50, example="Juanita")
    edad: int = Field(...,ge=1,le=123, description="Edad valida entre 1 y 123")



@app.get("/",tags=["Inicio"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def bienvenida():
    return {"mensaje": "¡Bienvenido a mi API!"}  # Formato JSON

@app.get("/HolaMundo",tags=["Bienvenida asincrona"])  # Endpoint
async def hola():
    await asyncio.sleep(7)#Simulacion de uns 
    return {"mensaje": "¡Hola Mundo FastAPI!",
            "estatus":"200"
            }  # Formato JSON

@app.get("/v1/parametroOb/{id}",tags=["Parametro Obligatorio"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def consultaUno(id:int):
    return {"Se encontró el usuario": id}  # Formato JSON

@app.get("/v1/parametroOp/",tags=["Parametro Opcional"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def consultaTodos(id:Optional[int]=None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return{"Mensaje": "Usuario encontrado", "Usuario": usuario}
        return{"Mensaje": "Usuario no encontrado", "Usuario": id}
    else:
        return{"Mensaje": "No se proporcionó ID"}
    
@app.get("/v1/usuarios/{id}",tags=["CRUD HTTP"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def leer_usuarios():
    return {
        "status":"200",
        "total": len(usuarios),
        "usuarios":usuarios
        }  # Formato JSON

@app.post("/v1/usuarios/",tags=["CRUD HTTP"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def crear_usuario(usuario:usuario_create):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario agregado",
        "Usuario":usuario
    }

@app.put("/v1/usuarios/{id}", tags=["CRUD HTTP"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def actualizar_usuario(usuario: dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            usuarios.append(usuario)
            return{
                "status":"200",
                "mensaje":"Usuario actualizado",
                "Usuario":usuario
            }
    raise HTTPException(
        status_code=400,
        detail="El id no existe, no se puede actualizar"
    )

@app.delete("/v1/usuarios/{id}", tags=["CRUD HTTP"])  # Endpoint de inicio, todos los endpoints se acompañan de una función
async def eliminar_usuario(usuario: dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            usuarios.remove(usuario)
            return{
                "status":"200",
                "mensaje":"Usuario eliminado",
                "Usuario":usuario
            }
    raise HTTPException(
        status_code=400,
        detail="El id no existe, no se puede eliminar"
    )