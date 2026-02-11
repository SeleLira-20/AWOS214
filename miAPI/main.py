# Importaciones
from fastapi import FastAPI
import asyncio
from typing import Optional

# Instancia del servidor
app = FastAPI(
    title="MI PRIMER API",
    description="Selene Guadalupe Lira Perez",
    version="1.0.0"
)

#TB ficticia
usuarios=[
    {"id":1, "nombre":"Estrella","edad":19},
    {"id":2, "nombre":"Carlos","edad":19},
    {"id":3, "nombre":"Isabella","edad":19},
]

# Endpoints
@app.get("/", tags=['Inicio'])
async def bienvenida():
    return {"mensaje": "¡Bienvenido a mi API!"}

@app.get("/HolaMundo", tags=["Bienvenida Asincrona"])
async def hola():
    await asyncio.sleep(3) 
    return {
        "mensaje": "¡Hola Mundo FastAPI!",
        "estatus": "200"
    }

@app.get("/V1/usuario/{id}", tags=['Parametro obligatorio'])
async def consultaUno(id:int):
    return {"Se regreso usuario": id }

@app.get("/V1/todos/usuarios", tags=['Parametro opcional'])
async def consultaTodos(id: Optional[int] = None):   
    if id is not None:
        # Buscar usuario por ID en la tabla
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"mensaje": "usuario encontrado", "usuario": usuario}
        return {"mensaje": "usuario no encontrado", "id": id}
    else:
        # Si no se proporciona ID, devolver todos los usuarios
        return {"mensaje": "Todos los usuarios", "usuarios": usuarios}