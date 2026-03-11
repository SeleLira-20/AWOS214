# IMPORTACIONES
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import secrets
import uuid

app = FastAPI(
    title="API de Tickets - Selene",
    description="API para control de tickets con autenticación",
    version="1.0"
)

# SEGURIDAD
security = HTTPBasic()
token_auth = HTTPBearer()

# usuario simulado
USUARIO = "Soporte"
PASSWORD = "4323"

# token almacenado
TOKENS_ACTIVOS = []

# BASE DE DATOS SIMULADA
tickets = []
contador_tickets = 1


# MODELOS
class TicketCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descripcion: str = Field(..., min_length=5)
    prioridad: str = Field(..., example="alta")


class Ticket(TicketCreate):
    id: int
    estado: str = "abierto"
    fecha_creacion: datetime


# AUTENTICACIÓN BASICA
def verificar_usuario(credentials: HTTPBasicCredentials = Depends(security)):

    usuario_correcto = secrets.compare_digest(credentials.username, USUARIO)
    password_correcto = secrets.compare_digest(credentials.password, PASSWORD)

    if not (usuario_correcto and password_correcto):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    return credentials.username


# GENERAR TOKEN
@app.post("/login", tags=["Autenticación"])
def login(usuario: str = Depends(verificar_usuario)):

    token = str(uuid.uuid4())
    TOKENS_ACTIVOS.append(token)

    return {
        "mensaje": "Autenticación correcta",
        "token": token
    }


# VALIDAR TOKEN
def validar_token(credentials: HTTPAuthorizationCredentials = Depends(token_auth)):

    token = credentials.credentials

    if token not in TOKENS_ACTIVOS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    return token


# ENDPOINT INICIO
@app.get("/", tags=["Inicio"])
def inicio():
    return {
        "mensaje": "Bienvenido a la API de Tickets",
        "login": "/login",
        "documentacion": "/docs"
    }


# CREAR TICKET
@app.post("/tickets", status_code=201, tags=["Tickets"])
def crear_ticket(ticket: TicketCreate, token: str = Depends(validar_token)):

    global contador_tickets

    nuevo_ticket = Ticket(
        id=contador_tickets,
        titulo=ticket.titulo,
        descripcion=ticket.descripcion,
        prioridad=ticket.prioridad,
        fecha_creacion=datetime.now()
    )

    tickets.append(nuevo_ticket)
    contador_tickets += 1

    return {
        "mensaje": "Ticket creado correctamente",
        "ticket": nuevo_ticket
    }


# LISTAR TICKETS
@app.get("/tickets", tags=["Tickets"])
def listar_tickets(token: str = Depends(validar_token)):

    return {
        "total": len(tickets),
        "tickets": tickets
    }


# BUSCAR TICKET
@app.get("/tickets/{id}", tags=["Tickets"])
def obtener_ticket(id: int, token: str = Depends(validar_token)):

    for ticket in tickets:
        if ticket.id == id:
            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket no encontrado"
    )


# CERRAR TICKET
@app.put("/tickets/{id}/cerrar", tags=["Tickets"])
def cerrar_ticket(id: int, token: str = Depends(validar_token)):

    for ticket in tickets:
        if ticket.id == id:
            ticket.estado = "cerrado"
            return {"mensaje": "Ticket cerrado"}

    raise HTTPException(
        status_code=404,
        detail="Ticket no encontrado"
    )


# ELIMINAR TICKET
@app.delete("/tickets/{id}", tags=["Tickets"])
def eliminar_ticket(id: int, token: str = Depends(validar_token)):

    for ticket in tickets:
        if ticket.id == id:
            tickets.remove(ticket)
            return {"mensaje": "Ticket eliminado"}

    raise HTTPException(
        status_code=404,
        detail="Ticket no encontrado"
    )