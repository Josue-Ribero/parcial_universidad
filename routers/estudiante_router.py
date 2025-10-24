from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.estudiante import Estudiante
from ..models.matricula import Matricula
from ..models.curso import Curso
from ..utils.enum import Semestre

router = APIRouter(prefix="/estudiante", tags=["Estudiantes"])

# CREATE - Crear estudiante
@router.post("/crear", response_model=Estudiante, status_code=201)
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
        raise HTTPException(400, "Ya hay un estudiante registrado con esa CC")
    
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



# READ - Obtener todos los estudiantes que hay
@router.get("/todos", response_model=list[Estudiante])
async def listaEstudiantes(session: SessionDep):
    listaEstudiantes = session.exec(select(Estudiante)).all()
    return listaEstudiantes



# READ - Obtener lista de estudiantes filtrados por semestre
@router.get("/semestre/{semestre}", response_model=list[Estudiante])
async def estudiantesPorSemestre(semestre: int, session: SessionDep):
    listaEstudiantes = session.exec(select(Estudiante).where(Estudiante.semestre == semestre)).all()
    return listaEstudiantes



# READ - Cursos de un estudiante
@router.get("/{estudianteID}/mis-cursos", response_model=list[Curso])
async def misCursos(estudianteID: int, session: SessionDep):
    listaMisCursos = session.exec(select(Curso).join(Matricula, Matricula.cursoID == Curso.id).where(Matricula.estudianteID == estudianteID)).all()
    return listaMisCursos