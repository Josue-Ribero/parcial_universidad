from fastapi import APIRouter, HTTPException, Form
from db.db import SessionDep
from sqlmodel import select
from ..models.curso import Curso, CursoCreate
from ..utils.enum import CreditosCurso, JornadaCurso

router = APIRouter(prefix="/curso", tags=["Cursos"])

# CREATE - Crear curso
@router.post("/crear", response_model=CursoCreate, status_code=201)
async def crearCurso(
    session: SessionDep,
    codigo: str = Form(...),
    nombre: str = Form(...),
    creditos: CreditosCurso = Form(...),
    jornada: JornadaCurso = Form(...)
    ):
    # Validar si el curso ya existe
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    if cursoDB:
        raise HTTPException(400, "El curso ingresado ya existe")
    
    # Si no existe, lo crea
    nuevoCurso = Curso(
        codigo=codigo,
        nombre=nombre,
        creditos=creditos,
        jornada=jornada
    )
    # Insertar el curso a la DB
    session.add(nuevoCurso)
    session.commit() # Guardar los cambios
    session.refresh(nuevoCurso)

    return nuevoCurso # Devuelve el objeto curso