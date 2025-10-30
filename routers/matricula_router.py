"""
Módulo: matricula_router
------------------------
Endpoints relacionados con la gestión de matrículas en el sistema académico.

Incluye operaciones para matricular, desmatricular, finalizar cursos, rematricular
y consultar las matrículas activas por estudiante o curso.
"""

from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from sqlalchemy import or_
from ..models.matricula import Matricula
from ..models.estudiante import Estudiante
from ..models.curso import Curso
from ..utils.enum import EstadoMatricula

router = APIRouter(prefix="/matricula", tags=["Matriculas"])

# CREATE - Crear matricula
@router.post("/matricular-estudiante", response_model=Matricula, status_code=201)
async def matricularEstudiante(
    session: SessionDep,
    codigo: str = Form(...),
    cedula: str = Form(...)
    ):

    """
    Matricular a un estudiante en un curso.

    Valida que el estudiante no esté ya matriculado en otro curso activo,
    y que no esté matriculado en el mismo curso con estado MATRICULADO.

    Args:
        session (SessionDep): Sesión de base de datos.
        codigo (str): Código del curso.
        cedula (str): Cédula del estudiante.

    Returns:
        Matricula: La matrícula creada o reactivada.

    Raises:
        HTTPException: 400 si hay conflictos de matrícula.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")
    
    # Verificar que el estudiante exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el estudiante
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
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

    """
    Obtener todas las matrículas activas (estado MATRICULADO).

    Args:
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Matricula]: Matrículas activas.
    """

    listaMatriculas = session.exec(select(Matricula).where(Matricula.matriculado == EstadoMatricula.MATRICULADO)).all()
    return listaMatriculas



# READ - Obtener un estudiante y sus cursos
@router.get("/estudiante/{cedula}", response_model=list[Matricula])
async def cursosDeEstudiante(cedula: str, session: SessionDep):

    """
    Obtener todas las matrículas de un estudiante.

    Args:
        cedula (str): Cédula del estudiante.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Matricula]: Matrículas del estudiante.

    Raises:
        HTTPException: 400 si la cédula no es válida, 404 si no tiene matrículas.
    """

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

    # Validar si el estudiante existe
    consulta = select(Matricula).where(Matricula.cedula == cedula)
    consulta = consulta.where(
        (Matricula.matriculado == EstadoMatricula.MATRICULADO) |
        (Matricula.matriculado == EstadoMatricula.FINALIZADO)
    )
    estudianteDB = session.exec(consulta).first()
    
    if not estudianteDB:
        raise HTTPException(404, "Estudiante sin matriculas activas")

    matriculaDB = session.exec(select(Matricula).where(Matricula.cedula == cedula)).all()
    if not matriculaDB:
        raise HTTPException(404, "No tienes cursos")
    return matriculaDB



# READ - Obtener un curso y sus estudiantes asociados
@router.get("/curso/{codigo}", response_model=list[Matricula])
async def estudiantesEnCurso(codigo: str, session: SessionDep):

    """
    Obtener todas las matrículas activas de un curso.

    Args:
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Matricula]: Matrículas activas del curso.

    Raises:
        HTTPException: 404 si no hay estudiantes matriculados.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")
    
    # Verificar que estudiantes estan en ese curso
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

    """
    Actualizar los datos de una matrícula.

    No permite modificar matrículas finalizadas.

    Args:
        session (SessionDep): Sesión de base de datos.
        matriculaID (int): ID de la matrícula a actualizar.
        codigo (str): Nuevo código del curso.
        cedula (str): Nueva cédula del estudiante.

    Returns:
        Matricula: Matrícula actualizada.

    Raises:
        HTTPException: 400 si ya existe o 404 si no se encuentra o está finalizada.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")
    
    # Verificar que el estudiante exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el estudiante
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")

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

    """
    Finalizar un curso por parte de un estudiante.

    Cambia el estado de la matrícula a FINALIZADO.

    Args:
        cedula (str): Cédula del estudiante.
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Matricula: Matrícula finalizada.

    Raises:
        HTTPException: 400 o 404 si no se encuentra o no está activa.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")
    
    # Verificar que el estudiante exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el estudiante
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

    """
    Rematricular a un estudiante en un curso previamente desmatriculado.

    Valida que no esté activo en otro curso ni haya finalizado el mismo.

    Args:
        cedula (str): Cédula del estudiante.
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Matricula: Matrícula reactivada.

    Raises:
        HTTPException: 400 si hay conflictos de estado.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")
    
    # Verificar que el estudiante exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el estudiante
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

    """
    Desmatricular a un estudiante de un curso.

    Cambia el estado de la matrícula a DESMATRICULADO.

    Args:
        cedula (str): Cédula del estudiante.
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Matricula: Matrícula desmatriculada.

    Raises:
        HTTPException: 400 o 404 si no se encuentra o no está activa.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener 7 caracteres")
    
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")
    
    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")
    
    # Verificar que el estudiante exista
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    # Si no existe el estudiante
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