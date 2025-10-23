from fastapi import APIRouter, HTTPException, Form
from db.db import SessionDep
from sqlmodel import select
from ..models.estudiante import Estudiante, EstudianteCreate
from ..utils.enum import Semestre

router = APIRouter(prefix="/estudiante", tags=["Estudiantes"])

# CREATE - Crear estudiante
@router.post("/crear", response_model=EstudianteCreate, status_code=201)
async def crearEstudiante(
    session: SessionDep,
    cedula: str = Form(...),
    nombre: str = Form(...),
    email: str = Form(...),
    semestre: Semestre = Form(...)
    ):
    # Validar si el estudiante ya existe
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    if estudianteDB:
        raise HTTPException(400, "El Estudiante ingresado ya existe")
    
    # Si no existe, lo crea
    nuevoEstudiante = Estudiante(
        cedula=cedula,
        nombre=nombre,
        email=email,
        semestre=semestre
    )
    # Insertar el estudiante a la DB
    session.add(nuevoEstudiante)
    session.commit() # Guardar los cambios
    session.refresh(nuevoEstudiante)

    return nuevoEstudiante # Devuelve el objeto estudiante