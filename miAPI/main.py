#importaciones 
from fastapi import FastAPI 
import asyncio 

#instancia del servidor 
app = FastAPI()

#Endpoints 
@app.get("/HolaMundo")
async def hola ():
     await asyncio.sleep(4)
     return{"mensaje": "¡Hola mundo fastAPI!"
            "status:""200"}