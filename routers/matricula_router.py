from fastapi import APIRouter, HTTPException, Form
from db.db import SessionDep
from sqlmodel import select
from ..models.matricula import Matricula, MatriculaCreate
from ..utils.enum import EstadoMatricula

router = APIRouter(prefix="/matricula", tags=["Matriculas"])

# CREATE - Crear matricula
@router.post("/matricular-estudiante", response_model=Matricula, status_code=201)
async def matricularEstudiante(
    session: SessionDep,
    cursoID: int = Form(...),
    estudianteID: int = Form(...),
    matriculado: EstadoMatricula = Form(...)
    ):
    # Validar si el matricula ya existe
    MatriculaDB = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.estudianteID == estudianteID)).first()
    if MatriculaDB:
        raise HTTPException(400, "El estudiante ya esta matriculado en ese curso")
    
    # Si no existe, lo crea
    nuevoMatricula = Matricula(
        cursoID=cursoID,
        estudianteID=estudianteID,
        matriculado=matriculado
    )
    # Insertar el matricula a la DB
    session.add(nuevoMatricula)
    session.commit() # Guardar los cambios
    session.refresh(nuevoMatricula)

    return nuevoMatricula # Devuelve el objeto matricula