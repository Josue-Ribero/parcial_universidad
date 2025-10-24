from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.matricula import Matricula
from ..utils.enum import EstadoMatricula

router = APIRouter(prefix="/matricula", tags=["Matriculas"])

# CREATE - Crear matricula
@router.post("/matricular-estudiante", response_model=Matricula, status_code=201)
async def matricularEstudiante(
    session: SessionDep,
    cursoID: int = Form(...),
    estudianteID: int = Form(...)
    ):
    # Validar si el matricula ya existe
    matriculaDB = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.estudianteID == estudianteID)).first()
    # Validar si el estudiante ya esta con estado MATRICULADO en ese curso
    if matriculaDB and matriculaDB.matriculado == EstadoMatricula.MATRICULADO:
        raise HTTPException(400, "El estudiante ya esta matriculado en ese curso")
    
    # Verificar si el estudiante ya esta matriculado en otro curso (esta activo)
    matriculadoEnOtroCurso = session.exec(select(Matricula).where(
        Matricula.estudianteID == estudianteID,
        Matricula.matriculado == EstadoMatricula.MATRICULADO,
        Matricula.cursoID != cursoID)
        ).first()
    # Si ya esta matriculado en otro curso
    if matriculadoEnOtroCurso:
        raise HTTPException(400, "El estudiante no puede estar registrado en mas de un curso a la vez")
    
    # Si ya existia pero estaba desmatriculado lo reactiva
    if matriculaDB and matriculaDB.matriculado == EstadoMatricula.DESMATRICULADO:
        matriculaDB.matriculado = EstadoMatricula.MATRICULADO
        session.add(matriculaDB)
        session.commit()
        session.refresh(matriculaDB)
        return matriculaDB
    
    # Si no esta matriculado, lo crea
    nuevaMatricula = Matricula(
        cursoID=cursoID,
        estudianteID=estudianteID,
        matriculado=EstadoMatricula.MATRICULADO
    )
    # Insertar el matricula a la DB
    session.add(nuevaMatricula)
    session.commit() # Guardar los cambios
    session.refresh(nuevaMatricula)

    return nuevaMatricula # Devuelve el objeto matricula



# READ - Obtener todos los matriculas que hay
@router.get("/todos", response_model=list[Matricula])
async def listaMatriculas(session: SessionDep):
    listaMatriculas = session.exec(select(Matricula).where(Matricula.matriculado == EstadoMatricula.MATRICULADO)).all()
    return listaMatriculas



# READ - Obtener un estudiante y sus cursos
@router.get("/estudiante/{estudianteID}", response_model=list[Matricula])
async def cursosDeEstudiante(estudianteID: int, session: SessionDep):
    estudianteDB = session.exec(select(Matricula).where(Matricula.estudianteID == estudianteID)).first()
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

    matriculaDB = session.exec(select(Matricula).where(Matricula.estudianteID == estudianteID)).all()
    if not matriculaDB:
        raise HTTPException(404, "No tienes cursos")
    return matriculaDB



# READ - Obtener un curso y sus estudiantes asociados
@router.get("/curso/{cursoID}", response_model=list[Matricula])
async def estudiantesEnCurso(cursoID: int, session: SessionDep):
    matriculaDB = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.matriculado == EstadoMatricula.MATRICULADO)).all()
    if not matriculaDB:
        raise HTTPException(404, "No hay estudiantes en este curso")
    return matriculaDB



# UPDATE - Actualizar matricula
@router.patch("/{matriculaID}/actualizar", response_model=Matricula)
async def actualizarMatricula(
    session: SessionDep,
    matriculaID: int,
    cursoID: int = Form(...),
    estudianteID: int = Form(...)
    ):

    # Verificar que exista la matricula
    matriculaDB = session.get(Matricula, matriculaID)
    if not matriculaDB:
        raise HTTPException(404, "La matricula no existe")

    # Verificar que no haya otra matricula con los id de estudiante y curso que ingresan
    existeMatricula = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.estudianteID == estudianteID)).first()
    if existeMatricula:
        raise HTTPException(400, "Ya existe esa matricula")
    
    # Actualizar los datos de la matricula
    matriculaDB.cursoID = cursoID
    matriculaDB.estudianteID = estudianteID

    # Insertar la matricula actualizada en la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB



# PATCH - Volver a matricular a un estudiante en un curso
@router.patch("/{estudianteID}/rematricular", response_model=Matricula)
async def rematricularEstudiante(estudianteID: int, cursoID: int, session: SessionDep):
    # Validar si ya existe una matricula
    matriculaDB = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.estudianteID == estudianteID)).first()
    # Si no existe la matricula
    if not matriculaDB:
        raise HTTPException(404, "Matricula no encontrada")
    
    # Validar si el estudiante ya habia sido matriculado en ese curso
    if matriculaDB.matriculado == EstadoMatricula.MATRICULADO:
        raise HTTPException(400, "El estudiante ya esta matriculado en ese curso")
    
    # Rematricular al estudiante si estaba desmatriculado
    matriculaDB.matriculado = EstadoMatricula.MATRICULADO
    # Insertar la matricula actualizada a la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB



# DELETE - Desmatricular a un estudiante de un curso
@router.delete("/{estudianteID}/desmatricular", response_model=Matricula)
async def desmatricularEstudiante(estudianteID: int, cursoID: int, session: SessionDep):
    # Validar si ya existe una matricula
    matriculaDB = session.exec(select(Matricula).where(Matricula.cursoID == cursoID, Matricula.estudianteID == estudianteID)).first()
    # Si no existe la matricula
    if not matriculaDB:
        raise HTTPException(404, "Matricula no encontrada")
    
    # Validar si el estudiante ya habia sido desmatriculado de ese curso
    if matriculaDB.matriculado == EstadoMatricula.DESMATRICULADO:
        raise HTTPException(400, "El estudiante ya habia sido desmatriculado")
    
    # Desmatricular al estudiante si no se habia hecho antes
    matriculaDB.matriculado = EstadoMatricula.DESMATRICULADO
    # Insertar la matricula actualizada a la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB