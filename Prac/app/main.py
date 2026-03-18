# Importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Instancia del servidor
app = FastAPI(
    title="Mi primer API",
    description="Selene Lira",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BD ficticia
productos = [
    {"id": 1, "nombre": "Laptop",  "precio": 15000.0, "stock": 10},
    {"id": 2, "nombre": "Mouse",   "precio": 350.0,   "stock": 50},
    {"id": 3, "nombre": "Teclado", "precio": 600.0,   "stock": 30},
]

# Modelo de validación Pydantic
class Producto(BaseModel):
    id:     int   = Field(..., gt=0,         description="ID único del producto")
    nombre: str   = Field(..., min_length=2, max_length=60, example="Monitor")
    precio: float = Field(..., gt=0,         description="Precio mayor a 0")
    stock:  int   = Field(..., ge=0,         description="Stock no puede ser negativo")

# ──────────────────────────────
# Seguridad HTTP Basic
# ──────────────────────────────
security = HTTPBasic()

def verificar_credenciales(credenciales: HTTPBasicCredentials = Depends(security)):
    usuario_ok  = secrets.compare_digest(credenciales.username, "SeleneLira")
    password_ok = secrets.compare_digest(credenciales.password, "123456")

    if not (usuario_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 👈 403 para evitar caché del navegador
            detail="Credenciales no autorizadas"
        )
    return credenciales.username

# ──────────────────────────────
# Endpoints generales
# ──────────────────────────────
@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "¡Bienvenido a mi API!"}

@app.get("/HolaMundo", tags=["Bienvenida Asincrona"])
async def hola():
    await asyncio.sleep(4)
    return {
        "mensaje": "¡Hola mundo FastAPI!",
        "estatus": "200"
    }

@app.get("/v1/parametroOp/{id}", tags=["Parametro obligatorio"])
async def consultaUno(id: int):
    return {"Se encontro producto": id}

@app.get("/v1/parametroOp/", tags=["Parametro opcional"])
async def consultaTodos(id: Optional[int] = None):
    if id is not None:
        for producto in productos:
            if producto["id"] == id:
                return {"mensaje": "producto encontrado", "producto": producto}
        return {"mensaje": "producto no encontrado", "id": id}
    else:
        return {"mensaje": "No se proporcionó id"}

# ──────────────────────────────
# CRUD
# ──────────────────────────────

# GET — leer todos
@app.get("/v1/productos/", tags=["CRUD HTTP"])
async def leer_productos():
    return {
        "status": "200",
        "total": len(productos),
        "productos": productos
    }

# GET — leer uno
@app.get("/v1/productos/{id}", tags=["CRUD HTTP"])
async def leer_producto(id: int):
    for producto in productos:
        if producto["id"] == id:
            return {"producto": producto}
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )

# POST — crear
@app.post("/v1/productos/", tags=["CRUD HTTP"], status_code=status.HTTP_201_CREATED)
async def crear_producto(producto: Producto):
    for p in productos:
        if p["id"] == producto.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )
    productos.append(producto.dict())
    return {
        "mensaje": "Producto creado",
        "producto": producto
    }

# PUT — actualizar (protegido 🔐)
@app.put("/v1/productos/{id}", tags=["CRUD HTTP"])
async def actualizar_producto(
    id: int,
    datos: Producto,
    userAuth: str = Depends(verificar_credenciales)
):
    for i in range(len(productos)):
        if productos[i]["id"] == id:
            productos[i] = datos.dict()
            return {
                "mensaje": f"Producto actualizado por: {userAuth}",
                "producto": productos[i]
            }
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )

# DELETE — eliminar (protegido 🔐)
@app.delete("/v1/productos/{id}", tags=["CRUD HTTP"], status_code=status.HTTP_200_OK)
async def eliminar_producto(
    id: int,
    userAuth: str = Depends(verificar_credenciales)
):
    for i in range(len(productos)):
        if productos[i]["id"] == id:
            eliminado = productos.pop(i)
            return {
                "mensaje": f"Producto eliminado por: {userAuth}",
                "producto": eliminado
            }
    raise HTTPException(
        status_code=404,
        detail="Producto no encontrado"
    )