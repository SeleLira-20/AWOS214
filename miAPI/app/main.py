from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional

# Instancia del servidor
app = FastAPI(
    title="Mi primer API",
    description="Selene Lira",
    version="1.0.0"
)

# Configurar CORS para permitir conexiones desde React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:19000",  # Para Expo
        "http://localhost:19001",  # Para Expo
        "http://10.0.2.2:5000",    # Para emulador Android
        "*"  # Solo para desarrollo, no usar en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tu código existente...
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

@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def leer_usuarios():
    return {
        "status": "200",
        "total": len(usuarios),
        "usuarios": usuarios
    }

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
    usuario["id"] = id
    
    for i in range(len(usuarios)):
        if usuarios[i]["id"] == id:
            usuarios[i] = usuario
            return {
                "mensaje": "Usuario actualizado",
                "Usuario": usuario
            }
    
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )

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
        status_code=404,
        detail="Usuario no encontrado"
    )