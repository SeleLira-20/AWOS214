from fastapi import FastAPI, status, HTTPException
import asyncio
from typing import Optional

# Instancia del servidor
app = FastAPI(
    title="Mi primer API",
    description="Selene Lira",
    version="1.0.0"
)

usuarios = [
    {"id": 1, "nombre": "Juan", "edad": 21},
    {"id": 2, "nombre": "Israel", "edad": 21},
    {"id": 3, "nombre": "Sofi", "edad": 21}
]

@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "¡Bienvenido a mi API!"}

@app.get("/HolaMundo", tags=["Bienvenida asincrona"])
async def hola():
    await asyncio.sleep(7)
    return {"mensaje": "¡Hola Mundo FastAPI!", "estatus": "200"}

@app.get("/v1/parametroOb/{id}", tags=["Parametro Obligatorio"])
async def consultaUno(id: int):
    return {"Se encontró el usuario": id}

@app.get("/v1/parametroOp/", tags=["Parametro Opcional"])
async def consultaTodos(id: Optional[int] = None):
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"Mensaje": "Usuario encontrado", "Usuario": usuario}
        return {"Mensaje": "Usuario no encontrado", "Usuario": id}
    else:
        return {"Mensaje": "No se proporcionó ID"}

# CORREGIDO: GET sin {id} en la ruta
@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def leer_usuarios():
    return {
        "status": "200",
        "total": len(usuarios),
        "usuarios": usuarios
    }

# CORREGIDO: POST sin {id} en la ruta
@app.post("/v1/usuarios/", tags=["CRUD HTTP"])
async def crear_usuario(usuario: dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    usuarios.append(usuario)
    return {
        "mensaje": "Usuario agregado",
        "Usuario": usuario
    }

@app.put("/v1/usuarios/{id}", tags=["CRUD HTTP"])
async def actualizar_usuario(id: int, usuario: dict):
    # Aseguramos que el ID en el body coincida con el de la URL
    usuario["id"] = id
    
    for i in range(len(usuarios)):
        if usuarios[i]["id"] == id:
            usuarios[i] = usuario
            return {
                "mensaje": "Usuario actualizado",
                "Usuario": usuario
            }
    
    raise HTTPException(
        status_code=202,
        detail="Usuario no encontrado"
    )

# NUEVO: Endpoint DELETE
@app.delete("/v1/usuarios/{id}", tags=["CRUD HTTP"])
async def eliminar_usuario(id: int):
    for i in range(len(usuarios)):
        if usuarios[i]["id"] == id:
            usuario_eliminado = usuarios.pop(i)
            return {
                "mensaje": "Usuario eliminado",
                "Usuario": usuario_eliminado
            }
    
    raise HTTPException(
        status_code=204,
        detail="Usuario no encontrado"
    )