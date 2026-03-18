from fastapi import FastAPI, status, HTTPException, Depends, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional

app = FastAPI(
    title="Examen Segundo Parcial - API de Tickets",
    description="API para gestión de tickets de soporte",
    version="1.0.0"
)

# SEGURIDAD - Basic Auth (Punto 8)
security = HTTPBasic()
USUARIO_SOPORTE = "soporte"
PASSWORD_SOPORTE = "4321"

def verificar_autenticacion(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verifica las credenciales del usuario para endpoints protegidos.
    """
    if credentials.username != USUARIO_SOPORTE or credentials.password != PASSWORD_SOPORTE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# BASE DE DATOS VOLÁTIL
db_tickets = []
id_counter = 1

# MODELOS (Punto 6)
class TicketBase(BaseModel):
    """Modelo base para crear un ticket."""
    nombre_usuario: str = Field(
        ..., 
        min_length=5, 
        max_length=50,
        description="Nombre del usuario (mínimo 5 caracteres)"
    )
    descripcion_problema: str = Field(
        ..., 
        min_length=20, 
        max_length=200,
        description="Descripción del problema (20-200 caracteres)"
    )
    prioridad: str = Field(
        ...,
        description="Prioridad del ticket: baja, media o alta"
    )

    @field_validator('prioridad')
    @classmethod
    def validar_prioridad(cls, v):
        """Valida que la prioridad sea baja, media o alta."""
        prioridad_lower = v.lower()
        if prioridad_lower not in ['baja', 'media', 'alta']:
            raise ValueError('La prioridad debe ser: baja, media o alta')
        return prioridad_lower

    @field_validator('nombre_usuario')
    @classmethod
    def validar_nombre_usuario(cls, v):
        """Valida que el nombre de usuario no esté vacío después de quitar espacios."""
        if not v.strip():
            raise ValueError('El nombre de usuario no puede estar vacío')
        return v.strip()

class Ticket(TicketBase):
    """Modelo completo de un ticket incluyendo campos del sistema."""
    id: int
    estado: str = Field(
        default="pendiente",
        description="Estado del ticket: pendiente o resuelto"
    )
    fecha_creacion: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nombre_usuario": "juan_perez",
                "descripcion_problema": "No puedo acceder al sistema con mi usuario",
                "prioridad": "alta",
                "estado": "pendiente",
                "fecha_creacion": "2024-01-01T10:30:00"
            }
        }

class TicketEstadoUpdate(BaseModel):
    """Modelo para actualizar solo el estado del ticket."""
    estado: str = Field(..., description="Nuevo estado: pendiente o resuelto")

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        """Valida que el estado sea pendiente o resuelto."""
        estado_lower = v.lower()
        if estado_lower not in ["pendiente", "resuelto"]:
            raise ValueError('El estado debe ser: pendiente o resuelto')
        return estado_lower

# --- ENDPOINTS ---

# 1. Crear ticket (Público)
@app.post(
    "/tickets", 
    response_model=Ticket, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ticket",
    description="Crea un nuevo ticket de soporte. Acceso público."
)
def crear_ticket(ticket_in: TicketBase):
    """
    Crea un nuevo ticket con los siguientes datos:
    - **nombre_usuario**: Mínimo 5 caracteres
    - **descripcion_problema**: Entre 20 y 200 caracteres
    - **prioridad**: baja, media o alta
    """
    global id_counter
    nuevo_ticket = Ticket(
        id=id_counter,
        nombre_usuario=ticket_in.nombre_usuario,
        descripcion_problema=ticket_in.descripcion_problema,
        prioridad=ticket_in.prioridad,  # Ya validado por el modelo
        estado="pendiente",
        fecha_creacion=datetime.now()
    )
    db_tickets.append(nuevo_ticket)
    id_counter += 1
    return nuevo_ticket

# 2. Listar tickets (Público)
@app.get(
    "/tickets", 
    response_model=List[Ticket],
    summary="Listar todos los tickets",
    description="Obtiene la lista completa de tickets. Acceso público."
)
def listar_tickets(
    estado: Optional[str] = Query(None, description="Filtrar por estado (pendiente/resuelto)"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad (baja/media/alta)")
):
    """
    Lista todos los tickets. Opcionalmente puede filtrar por estado o prioridad.
    """
    tickets = db_tickets.copy()
    
    # Aplicar filtros si se proporcionan
    if estado:
        estado_lower = estado.lower()
        if estado_lower not in ["pendiente", "resuelto"]:
            raise HTTPException(
                status_code=400, 
                detail="Estado inválido. Use: pendiente o resuelto"
            )
        tickets = [t for t in tickets if t.estado == estado_lower]
    
    if prioridad:
        prioridad_lower = prioridad.lower()
        if prioridad_lower not in ["baja", "media", "alta"]:
            raise HTTPException(
                status_code=400, 
                detail="Prioridad inválida. Use: baja, media o alta"
            )
        tickets = [t for t in tickets if t.prioridad == prioridad_lower]
    
    return tickets

# 3. Consultar por ID (PROTEGIDO - Punto 8)
@app.get(
    "/tickets/{ticket_id}", 
    response_model=Ticket,
    summary="Consultar ticket por ID",
    description="Obtiene un ticket específico por su ID. Requiere autenticación."
)
def consultar_por_id(
    ticket_id: int, 
    user: str = Depends(verificar_autenticacion)
):
    """
    Consulta un ticket específico por su ID.
    - **ticket_id**: ID del ticket a consultar
    """
    for t in db_tickets:
        if t.id == ticket_id:
            return t
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Ticket con ID {ticket_id} no encontrado"
    )

# 4. Cambiar estado (PROTEGIDO - Punto 8)
@app.patch(
    "/tickets/{ticket_id}/estado",
    summary="Cambiar estado de un ticket",
    description="Actualiza el estado de un ticket. Requiere autenticación."
)
def cambiar_estado(
    ticket_id: int, 
    estado_update: TicketEstadoUpdate,
    user: str = Depends(verificar_autenticacion)
):
    """
    Cambia el estado de un ticket específico.
    - **ticket_id**: ID del ticket a actualizar
    - **estado**: Nuevo estado (pendiente/resuelto)
    """
    for t in db_tickets:
        if t.id == ticket_id:
            t.estado = estado_update.estado
            return {
                "mensaje": f"Ticket {ticket_id} actualizado exitosamente",
                "nuevo_estado": estado_update.estado
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Ticket con ID {ticket_id} no encontrado"
    )

# 5. Eliminar ticket (Público, con restricción Punto 7)
@app.delete(
    "/tickets/{ticket_id}",
    summary="Eliminar un ticket",
    description="Elimina un ticket. No se pueden eliminar tickets con estado 'resuelto'."
)
def eliminar_ticket(ticket_id: int):
    """
    Elimina un ticket específico.
    - **ticket_id**: ID del ticket a eliminar
    
    **Nota**: No se permite eliminar tickets con estado 'resuelto'.
    """
    for index, t in enumerate(db_tickets):
        if t.id == ticket_id:
            # No permitir eliminar si está RESUELTO (Punto 7)
            if t.estado == "resuelto":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="No se pueden eliminar tickets con estado 'Resuelto'"
                )
            # Eliminar el ticket y devolverlo
            ticket_eliminado = db_tickets.pop(index)
            return {
                "mensaje": f"Ticket {ticket_id} eliminado exitosamente",
                "ticket_eliminado": ticket_eliminado
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Ticket con ID {ticket_id} no encontrado"
    )

# Endpoint adicional para obtener estadísticas (opcional)
@app.get(
    "/tickets/estadisticas/resumen",
    summary="Obtener resumen de tickets",
    description="Obtiene estadísticas básicas de los tickets. Requiere autenticación."
)
def obtener_estadisticas(user: str = Depends(verificar_autenticacion)):
    """
    Obtiene un resumen estadístico de los tickets:
    - Total de tickets
    - Tickets por estado
    - Tickets por prioridad
    """
    total = len(db_tickets)
    pendientes = sum(1 for t in db_tickets if t.estado == "pendiente")
    resueltos = sum(1 for t in db_tickets if t.estado == "resuelto")
    
    por_prioridad = {
        "baja": sum(1 for t in db_tickets if t.prioridad == "baja"),
        "media": sum(1 for t in db_tickets if t.prioridad == "media"),
        "alta": sum(1 for t in db_tickets if t.prioridad == "alta")
    }
    
    return {
        "total_tickets": total,
        "por_estado": {
            "pendientes": pendientes,
            "resueltos": resueltos
        },
        "por_prioridad": por_prioridad
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)