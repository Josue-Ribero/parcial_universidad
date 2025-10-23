from fastapi import APIRouter, HTTPException, Form
from db.db import SessionDep
from sqlmodel import select
from ..models.curso import Curso, CursoCreate
from ..utils.enum import CreditosCurso, JornadaCurso

router = APIRouter(prefix="/curso", tags=["Cursos"])

# CREATE - Crear curso
@router.post("/crear", response_model=Curso, status_code=201)
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



# READ - Obtener todos los cursos que hay
@router.get("/todos", response_model=list[Curso])
async def listaCursos(session: SessionDep):
    listaCursos = session.exec(select(Curso)).all()
    return listaCursos



# READ - Obtener el curso filtrado por codigo
@router.get("/codigo/{codigo}", response_model=list[Curso])
async def listaCursos(codigo: int, session: SessionDep):
    cursoDB = session.get(Curso, codigo)
    return cursoDB



# READ - Obtener lista de cursos filtrados por creditos
@router.get("/creditos/{creditos}", response_model=list[Curso])
async def listaCursos(creditos: int, session: SessionDep):
    listaCursos = session.exec(select(Curso)).all()
    return listaCursos