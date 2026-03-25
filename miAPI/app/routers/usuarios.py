from fastapi import status, HTTPException, Depends, APIRouter
from app.models.usuario import usuario_create
from app.data.database import usuarios 
from app.security.auth import verificar_Peticion

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import Usuario as usuarioDB

router = APIRouter(
    prefix= "/v1/usuarios", tags=["CRUD HTTP"]
)

@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    queryUsers = db.query(usuarioDB).all()
    return {
        "status": "200",
        "total": len(queryUsers),
        "usuarios": queryUsers
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: usuario_create, db: Session = Depends(get_db)):
    nuevoUsuario = usuarioDB(nombre=usuario.nombre, edad=usuario.edad)  # ✅ "usuarioP" → "usuario"
    db.add(nuevoUsuario)
    db.commit()
    db.refresh(nuevoUsuario)

    return {
        "mensaje": "Usuario agregado",
        "Usuario": usuario  # ✅ "usuarioP" → "usuario"
    }

@router.put("/{id_buscado}")
async def actualizar_usuario(id_buscado: int, datos_nuevos: dict, db: Session = Depends(get_db)):
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id_buscado).first()  # ✅ migrado a DB
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    for key, value in datos_nuevos.items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    
    return {
        "mensaje": "Usuario actualizado",
        "usuario": usuario
    }

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, db: Session = Depends(get_db), userAuth: str = Depends(verificar_Peticion)):
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()  # ✅ migrado a DB
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    
    return {
        "message": f"Usuario eliminado por: {userAuth}"  # ✅ "messege" → "message"
    }