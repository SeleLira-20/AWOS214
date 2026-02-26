from fastapi import FastAPI, status, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

app = FastAPI(
    title="Biblioteca Digital API de Selene",
    description="API para control de biblioteca digital - Repaso",
    version="1.0.0"
)


libros = []          
prestamos = []       
contador_libros = 1  
contador_prestamos = 1  

class Usuario(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, example="Juan Pérez")
    email: str = Field(..., example="juan@email.com")
    
    @validator('email')
    def email_valido(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Email no válido')
        return v

class LibroCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, example="Cien años de soledad")
    autor: str = Field(..., min_length=2, max_length=100, example="Gabriel García Márquez")
    anio: int = Field(..., example=1967)
    paginas: int = Field(..., gt=1, example=471)
    
    @validator('anio')
    def anio_valido(cls, v):
        año_actual = datetime.now().year
        if v <= 1450:
            raise ValueError('El año debe ser mayor a 1450')
        if v > año_actual:
            raise ValueError(f'El año no puede ser mayor a {año_actual}')
        return v

class Libro(LibroCreate):
    id: int
    estado: str = "disponible"  # disponible o prestado

class PrestamoCreate(BaseModel):
    libro_id: int = Field(..., example=1)
    usuario: Usuario

class Prestamo(PrestamoCreate):
    id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None
    activo: bool = True

#  ENDPOINTS 

@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {
        "mensaje": "¡Bienvenido a la API de Biblioteca Digital!",
        "endpoints": {
            "POST /libros": "Registrar un libro",
            "GET /libros": "Listar todos los libros disponibles",
            "GET /libros/buscar/{nombre}": "Buscar libro por nombre",
            "POST /prestamos": "Registrar préstamo",
            "PUT /prestamos/{id}/devolver": "Marcar libro como devuelto",
            "DELETE /prestamos/{id}": "Eliminar registro de préstamo"
        }
    }

# a. Registrar un libro
@app.post("/libros", status_code=status.HTTP_201_CREATED, tags=["Libros"])
async def registrar_libro(libro: LibroCreate):
    global contador_libros
    
    # Validar que el nombre no esté vacío (400 Request)
    if not libro.nombre or len(libro.nombre.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del libro no es válido"
        )
    
    nuevo_libro = Libro(
        id=contador_libros,
        **libro.dict()
    )
    libros.append(nuevo_libro)
    contador_libros += 1
    
    return {
        "status": "201",
        "mensaje": "Libro registrado exitosamente",
        "libro": nuevo_libro
    }

# b. Listar todos los libros disponibles
@app.get("/libros", tags=["Libros"])
async def listar_libros(disponibles: Optional[bool] = None):
    if disponibles is True:
        libros_filtrados = [l for l in libros if l.estado == "disponible"]
        return {
            "status": "200",
            "total": len(libros_filtrados),
            "libros": libros_filtrados
        }
    elif disponibles is False:
        libros_filtrados = [l for l in libros if l.estado == "prestado"]
        return {
            "status": "200",
            "total": len(libros_filtrados),
            "libros": libros_filtrados
        }
    else:
        return {
            "status": "200",
            "total": len(libros),
            "libros": libros
        }

# c. Buscar un libro por su nombre
@app.get("/libros/buscar/{nombre}", tags=["Libros"])
async def buscar_por_nombre(nombre: str):
    # Validar que el nombre no esté vacío (400 Request)
    if not nombre or len(nombre.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de búsqueda no es válido"
        )
    
    resultados = []
    for libro in libros:
        if nombre.lower() in libro.nombre.lower():
            resultados.append(libro)
    
    return {
        "status": "200",
        "busqueda": nombre,
        "total": len(resultados),
        "libros": resultados
    }

# d. Registrar el préstamo de un libro a un usuario
@app.post("/prestamos", status_code=status.HTTP_201_CREATED, tags=["Préstamos"])
async def registrar_prestamo(prestamo: PrestamoCreate):
    global contador_prestamos
    
    # Buscar el libro
    libro_encontrado = None
    for libro in libros:
        if libro.id == prestamo.libro_id:
            libro_encontrado = libro
            break
    
    # 404 si el libro no existe
    if not libro_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    
    # 409 Conflict si el libro ya está prestado
    if libro_encontrado.estado == "prestado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El libro ya está prestado"
        )
    
    # Actualizar estado del libro
    libro_encontrado.estado = "prestado"
    
    # Crear préstamo
    nuevo_prestamo = Prestamo(
        id=contador_prestamos,
        **prestamo.dict(),
        fecha_prestamo=datetime.now()
    )
    prestamos.append(nuevo_prestamo)
    contador_prestamos += 1
    
    return {
        "status": "201",
        "mensaje": "Préstamo registrado exitosamente",
        "prestamo": nuevo_prestamo
    }

# e. Marcar un libro como devuelto
@app.put("/prestamos/{id}/devolver", tags=["Préstamos"])
async def devolver_libro(id: int):
    # Buscar el préstamo
    prestamo_encontrado = None
    for prestamo in prestamos:
        if prestamo.id == id:
            prestamo_encontrado = prestamo
            break
    
    # 404 si el préstamo no existe
    if not prestamo_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    # 409 Conflict si el préstamo ya no existe (ya fue devuelto/eliminado)
    if not prestamo_encontrado.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El registro de préstamo ya no existe"
        )
    
    # Buscar y actualizar el libro
    for libro in libros:
        if libro.id == prestamo_encontrado.libro_id:
            libro.estado = "disponible"
            break
    
    # Actualizar préstamo
    prestamo_encontrado.activo = False
    prestamo_encontrado.fecha_devolucion = datetime.now()
    
    return {
        "status": "200",
        "mensaje": "Libro devuelto exitosamente",
        "prestamo_id": id
    }

# f. Eliminar el registro de un préstamo
@app.delete("/prestamos/{id}", tags=["Préstamos"])
async def eliminar_prestamo(id: int):
    # Buscar el préstamo
    prestamo_encontrado = None
    for prestamo in prestamos:
        if prestamo.id == id:
            prestamo_encontrado = prestamo
            break
    
    # 404 si el préstamo no existe
    if not prestamo_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    # 409 Conflict si el préstamo ya no existe
    if not prestamo_encontrado.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El registro de préstamo ya no existe"
        )
    
    # Si está activo, devolver el libro
    if prestamo_encontrado.activo:
        for libro in libros:
            if libro.id == prestamo_encontrado.libro_id:
                libro.estado = "disponible"
                break
    
    # Eliminar lógicamente el préstamo
    prestamo_encontrado.activo = False
    prestamo_encontrado.fecha_devolucion = datetime.now()
    
    return {
        "status": "200",
        "mensaje": "Registro de préstamo eliminado exitosamente",
        "prestamo_id": id
    }

# Endpoint adicional para ver todos los préstamos
@app.get("/prestamos", tags=["Préstamos"])
async def listar_prestamos(activos: Optional[bool] = None):
    if activos is True:
        prestamos_filtrados = [p for p in prestamos if p.activo]
        return {
            "status": "200",
            "total": len(prestamos_filtrados),
            "prestamos": prestamos_filtrados
        }
    elif activos is False:
        prestamos_filtrados = [p for p in prestamos if not p.activo]
        return {
            "status": "200",
            "total": len(prestamos_filtrados),
            "prestamos": prestamos_filtrados
        }
    else:
        return {
            "status": "200",
            "total": len(prestamos),
            "prestamos": prestamos
        }

# Endpoint para obtener un libro específico
@app.get("/libros/{id}", tags=["Libros"])
async def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return {
                "status": "200",
                "libro": libro
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Libro no encontrado"
    )