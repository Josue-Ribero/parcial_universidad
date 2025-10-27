from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.matricula import Matricula
from ..models.estudiante import Estudiante
from ..utils.enum import EstadoMatricula

router = APIRouter(prefix="/matricula", tags=["Matriculas"])

# CREATE - Crear matricula
@router.post("/matricular-estudiante", response_model=Matricula, status_code=201)
async def matricularEstudiante(
    session: SessionDep,
    codigo: str = Form(...),
    cedula: str = Form(...)
    ):

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

    # Validar si el matricula ya existe
    matriculaDB = session.exec(select(Matricula).where(Matricula.codigo == codigo, Matricula.cedula == cedula)).first()
    # Validar si el estudiante ya esta con estado MATRICULADO en ese curso
    if matriculaDB and matriculaDB.matriculado == EstadoMatricula.MATRICULADO:
        raise HTTPException(400, "El estudiante ya esta matriculado en ese curso")
    
    # Verificar si el estudiante ya esta matriculado en otro curso (esta activo)
    matriculadoEnOtroCurso = session.exec(select(Matricula).where(
        Matricula.cedula == cedula,
        Matricula.matriculado == EstadoMatricula.MATRICULADO,
        Matricula.codigo != codigo)
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
        codigo=codigo,
        cedula=cedula,
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
@router.get("/estudiante/{cedula}", response_model=list[Matricula])
async def cursosDeEstudiante(cedula: str, session: SessionDep):
    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")

    # Validar si ya existe el estudiante
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe la matricula
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

    # Validar si el estudiante existe
    estudianteDB = session.exec(select(Matricula).where(Matricula.cedula == cedula, Matricula.matriculado == EstadoMatricula.MATRICULADO)).first()
    if not estudianteDB:
        raise HTTPException(404, "Estudiante sin matriculas")

    matriculaDB = session.exec(select(Matricula).where(Matricula.cedula == cedula)).all()
    if not matriculaDB:
        raise HTTPException(404, "No tienes cursos")
    return matriculaDB



# READ - Obtener un curso y sus estudiantes asociados
@router.get("/curso/{codigo}", response_model=list[Matricula])
async def estudiantesEnCurso(codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    matriculaDB = session.exec(select(Matricula).where(Matricula.codigo == codigo, Matricula.matriculado == EstadoMatricula.MATRICULADO)).all()
    if not matriculaDB:
        raise HTTPException(404, "No hay estudiantes en este curso")
    return matriculaDB



# UPDATE - Actualizar matricula
@router.patch("/{matriculaID}/actualizar", response_model=Matricula)
async def actualizarMatricula(
    session: SessionDep,
    matriculaID: int,
    codigo: str = Form(...),
    cedula: str = Form(...)
    ):

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

    # Verificar que exista la matricula
    matriculaDB = session.get(Matricula, matriculaID)
    if not matriculaDB:
        raise HTTPException(404, "La matricula no existe")
    
    # No permitir que se modifique una matricula finalizada
    if matriculaDB.matriculado == EstadoMatricula.FINALIZADO:
        raise HTTPException(404, "No puedes modificar esta matricula por que fue finalizada")

    # Verificar que no haya otra matricula con los id de estudiante y curso que ingresan
    existeMatricula = session.exec(
        select(Matricula).where(
            Matricula.codigo == codigo,
            Matricula.cedula == cedula,
            Matricula.matriculado == EstadoMatricula.MATRICULADO
            )
        ).first()
    # Si existe la matricula
    if existeMatricula:
        raise HTTPException(400, "Ya existe esa matricula")
    
    # Actualizar los datos de la matricula
    matriculaDB.codigo = codigo
    matriculaDB.cedula = cedula

    # Insertar la matricula actualizada en la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB



# PATCH - Finalizacion de un curso por parte de un estudiante
@router.patch("/{cedula}/finalizar", response_model=Matricula)
async def finalizarCurso(cedula: str, codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

    # Validar si ya existe el estudiante
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe la matricula
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

    # Validar si ya existe una matricula
    matriculaDB = session.exec(
        select(Matricula).where(
            Matricula.codigo == codigo,
            Matricula.cedula == cedula,
            Matricula.matriculado == EstadoMatricula.MATRICULADO
            )
        ).first()
    
    # Si no existe la matricula
    if not matriculaDB:
        raise HTTPException(404, "Matricula no encontrada")
    
    # Finalizar el curso si esta matriculado
    if matriculaDB.matriculado == EstadoMatricula.MATRICULADO:
        matriculaDB.matriculado = EstadoMatricula.FINALIZADO
    
    # Insertar la matricula actualizada a la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB



# PATCH - Volver a matricular a un estudiante en un curso
@router.patch("/{cedula}/rematricular", response_model=Matricula)
async def rematricularEstudiante(cedula: str, codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

    # Validar si ya existe el estudiante
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe la matricula
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

    # Validar si ya existe una matricula
    matriculaDB = session.exec(select(Matricula).where(Matricula.codigo == codigo, Matricula.cedula == cedula)).first()
    # Si no existe la matricula
    if not matriculaDB:
        raise HTTPException(404, "Matricula no encontrada")
    
    # Verificar si el estudiante ya esta matriculado en otro curso (esta activo)
    matriculadoEnOtroCurso = session.exec(select(Matricula).where(
        Matricula.cedula == cedula,
        Matricula.matriculado == EstadoMatricula.MATRICULADO,
        Matricula.codigo != codigo)
        ).first()
    # Si ya esta matriculado en otro curso
    if matriculadoEnOtroCurso:
        raise HTTPException(400, "El estudiante no puede estar registrado en mas de un curso a la vez")
    
    # Validar si el estudiante ya habia sido matriculado en ese curso
    if matriculaDB.matriculado == EstadoMatricula.MATRICULADO:
        raise HTTPException(400, "El estudiante ya esta matriculado en ese curso")
    
    # Validar si el estudiante ya finalizo el cuso
    if matriculaDB.matriculado == EstadoMatricula.FINALIZADO:
        raise HTTPException(400, "El estudiante ya hizo este curso. No puede repetirlo")
    
    # Rematricular al estudiante si estaba desmatriculado
    matriculaDB.matriculado = EstadoMatricula.MATRICULADO
    # Insertar la matricula actualizada a la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB



# DELETE - Desmatricular a un estudiante de un curso
@router.delete("/{cedula}/desmatricular", response_model=Matricula)
async def desmatricularEstudiante(cedula: str, codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

    # Validar si ya existe el estudiante
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe la matricula
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

    # Validar si ya existe una matricula
    matriculaDB = session.exec(
        select(Matricula).where(
            Matricula.codigo == codigo,
            Matricula.cedula == cedula,
            Matricula.matriculado == EstadoMatricula.MATRICULADO
            )
        ).first()
    # Si no existe la matricula
    if not matriculaDB:
        raise HTTPException(404, "Matricula no encontrada")
    
    # Desmatricular al estudiante si no se habia hecho antes
    matriculaDB.matriculado = EstadoMatricula.DESMATRICULADO
    # Insertar la matricula actualizada a la DB
    session.add(matriculaDB)
    session.commit() # Guardar los cambios
    session.refresh(matriculaDB)

    return matriculaDB