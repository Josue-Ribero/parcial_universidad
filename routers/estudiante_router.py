from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.estudiante import Estudiante, EstudianteHistorico
from ..models.matricula import Matricula, MatriculaHistorica
from ..models.curso import Curso
from ..utils.enum import Semestre, EstadoMatricula

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
    
    # Convertir el nombre a mayusculas
    nombre = nombre.upper()

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
    # Si no hay estudiantes
    if len(listaEstudiantes) == 0:
        raise HTTPException(404, "No hay estudiantes")
    
    return listaEstudiantes



# READ - Obtener lista de estudiantes filtrados por semestre
@router.get("/semestre/{semestre}", response_model=list[Estudiante])
async def estudiantesPorSemestre(semestre: Semestre, session: SessionDep):
    listaEstudiantes = session.exec(select(Estudiante).where(Estudiante.semestre == semestre)).all()
    # Si no hay estudiantes en ese semestre
    if len(listaEstudiantes) == 0:
        raise HTTPException(404, "No hay estudiantes en ese semestre")
    
    return listaEstudiantes



# READ - Obtener un estudiante filtrado por semestre y email
@router.get("/{semestre}/{email}", response_model=Estudiante)
async def estudiantesPorSemestre(semestre: Semestre, email: str, session: SessionDep):
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.semestre == semestre, Estudiante.email == email)).first()
    # Si no existe un estudiante con ese email
    if not estudianteDB:
        raise HTTPException(404, f"Estudiante con email {email} no esta en el semestre {semestre}")
    
    return estudianteDB



# READ - Cursos de un estudiante
@router.get("/{cedula}/mis-cursos", response_model=list[Curso])
async def misCursos(cedula: str, session: SessionDep):
    listaMisCursos = session.exec(
        select(Curso)
            .join(Matricula, Matricula.codigo == Curso.codigo)
            .where(Matricula.cedula == cedula, Matricula.matriculado == EstadoMatricula.MATRICULADO)
        ).all()
    # Si el estudiante no tiene cursos
    if len(listaMisCursos) == 0:
        raise HTTPException(404, "No tienes cursos")
    
    return listaMisCursos



# READ - Cursos de un estudiante
@router.get("/{cedula}/mis-cursos", response_model=list[Curso])
async def misCursos(cedula: str, session: SessionDep):
    listaMisCursos = session.exec(
        select(Curso)
            .join(Matricula, Matricula.codigo == Curso.codigo)
            .where(Matricula.cedula == cedula, Matricula.matriculado == EstadoMatricula.MATRICULADO)
        ).all()
    # Si el estudiante no tiene cursos
    if len(listaMisCursos) == 0:
        raise HTTPException(404, "No tienes cursos")
    
    return listaMisCursos



# UPDATE - Actualizar el semestre de un estudiante
@router.patch("/{cedula}/actualizar", response_model=Estudiante)
async def actualizarJornadaCurso(session: SessionDep, cedula: str, semestre: Semestre = Form(...)):
    # Verificar que el curso exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el curso
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
    # Cambiar la jornada del curso
    estudianteDB.semestre = semestre
    #Insertar curso actualizado en la DB
    session.add(estudianteDB)
    session.commit() # Guardar los cambios
    session.refresh(estudianteDB)
    
    return estudianteDB



# DELETE - Eliminar un estudiante
@router.delete("/{cedula}/eliminar")
async def eliminarEstudiante(cedula: str, session: SessionDep):
    # Validar si ya existe el estudiante
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe la matricula
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
    # Guardar matrículas relacionadas en el histórico antes de borrar
    matriculasDB = session.exec(select(Matricula).where(Matricula.cedula == cedula)).all()
    for matricula in matriculasDB:
        matriculaHistorica = MatriculaHistorica(
            codigo=matricula.codigo,
            cedula=matricula.cedula,
            matriculado=matricula.matriculado,
            razonEliminado="Estudiante eliminado"
        )
        # Insertar las matriculas del curso al historico
        session.add(matriculaHistorica)
    session.commit() # Guardar los cambios
    
    # Copiar a estudiante historico
    estudianteHistorico = EstudianteHistorico(
        cedula=estudianteDB.cedula,
        nombre=estudianteDB.nombre,
        email=estudianteDB.email,
        semestre=estudianteDB.semestre
    )
    session.add(estudianteHistorico)
    
    # Eliminar el estudiante de la DB
    session.delete(estudianteDB)
    session.commit() # Guardar los cambios

    return {"Mensaje": "Estudiante eliminado correctamente"}