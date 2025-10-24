from fastapi import FastAPI
from .db.db import createAllTables
from .routers import (
    curso_router,
    estudiante_router,
    matricula_router
)

# Crear la instancia de FastAPI
app = FastAPI(lifespan=createAllTables, title="Gestor de Universidad", version="0.0.1")

# Incluir los routers en la app
app.include_router(curso_router.router)
app.include_router(estudiante_router.router)
app.include_router(matricula_router.router)

# Ruta de inicio
@app.get("/")
async def inicio():
    return {"mensaje" : "Bienvenido al gestor de universidad"}