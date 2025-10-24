from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.curso import Curso, CursoUpdate
from ..models.matricula import Matricula
from ..models.estudiante import Estudiante
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
        raise HTTPException(400, "Ya hay un curso registrado con ese codigo")
    
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
    # Si no hay cursos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos")
    
    return listaCursos



# READ - Obtener el curso filtrado por codigo
@router.get("/codigo/{codigo}", response_model=Curso)
async def cursosPorCodigo(codigo: str, session: SessionDep):
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso con ese codigo
    if not cursoDB:
        raise HTTPException(404, "No existe ese curso")
    
    return cursoDB



# READ - Obtener lista de cursos filtrados por creditos
@router.get("/creditos/{creditos}", response_model=list[Curso])
async def cursosPorCreditos(session: SessionDep, creditos: CreditosCurso):
    listaCursos = session.exec(select(Curso).where(Curso.creditos == creditos)).all()
    # Si no hay cursos con esos creditos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos con esa cantidad de creditos")
    
    return listaCursos



# READ - Estudiantes matriculados en un curso
@router.get("/{cursoID}/estudiantes", response_model=list[Estudiante])
async def estudiantesPorCurso(cursoID: int, session: SessionDep):
    estudiantesEnCurso = session.exec(select(Estudiante).join(Matricula, Matricula.estudianteID == Estudiante.id).where(Matricula.cursoID == cursoID)).all()
    # Si no hay estudiantes en ese curso
    if len(estudiantesEnCurso) == 0:
        raise HTTPException(404, "No hay estudiantes en ese curso")
    
    return estudiantesEnCurso



# UPDATE - Actualizar la jornada de un curso
@router.patch("/{codigo}/actualizar", response_model=Curso)
async def actualizarJornadaCurso(session: SessionDep, codigo: str, jornada: JornadaCurso = Form(...)):
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, "Curso no encontrado")
    
    # Cambiar la jornada del curso
    cursoDB.jornada = jornada
    #Insertar curso actualizado en la DB
    session.add(cursoDB)
    session.commit() # Guardar los cambios
    session.refresh(cursoDB)
    
    return cursoDB