#Importaciones
from fastapi import FastAPI
from app.routers import usuarios,varios

#instancia del servidor 
app = FastAPI(
    title="Mi primer API",
    description="Selene lira",
    version="1.0.0"
    )

app.include_router(usuarios.router)
app.include_router(varios.router)








