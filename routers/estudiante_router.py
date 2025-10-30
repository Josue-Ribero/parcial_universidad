"""
Módulo: estudiante_router
-------------------------
Endpoints relacionados con la gestión de estudiantes en el sistema académico.

Permite crear, consultar, actualizar y eliminar estudiantes, así como consultar
los cursos en los que están matriculados y filtrar por diversos criterios.
"""

from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.estudiante import Estudiante, EstudianteHistorico
from ..models.matricula import Matricula, MatriculaHistorica
from ..models.curso import Curso
from sqlalchemy import or_
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

    """
    Crear un nuevo estudiante.

    Valida que la cédula sea numérica y única, y que tenga entre 7 y 10 dígitos.
    Convierte el nombre a mayúsculas y el email a minúsculas.

    Args:
        session (SessionDep): Sesión de base de datos.
        cedula (str): Cédula del estudiante.
        nombre (str): Nombre completo del estudiante.
        email (str): Email del estudiante.
        semestre (Semestre): Semestre académico actual.

    Returns:
        Estudiante: El estudiante creado.

    Raises:
        HTTPException: 400 si la cédula ya existe o no es válida.
    """

    # Validar si el estudiante ya existe
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.cedula == cedula)).first()
    if estudianteDB:
        raise HTTPException(400, "Ya hay un estudiante registrado con esa CC")
    
    # Convertir el nombre a mayusculas
    nombre = nombre.upper()

    # Convertir el nombre a mayusculas
    email = email.lower()

    # Validar que el correo sea @ucatolica.edu.co
    if "@ucatolica.edu.co" not in email:
        raise HTTPException(400, "El email debe tener dominio ucatolica.edu.co")

    # Validar que la cedula sea numerica
    if not cedula.isdigit():
        raise HTTPException(400, "La cedula debe ser numerica")

    # Validar que la CC sea valida
    if not 7 <= len(cedula) <= 10:
        raise HTTPException(400, "La cedula debe tener entre 7 y 10 numeros")

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

    """
    Obtener todos los estudiantes registrados.

    Args:
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Estudiante]: Lista de todos los estudiantes.

    Raises:
        HTTPException: 404 si no hay estudiantes.
    """

    listaEstudiantes = session.exec(select(Estudiante)).all()
    # Si no hay estudiantes
    if len(listaEstudiantes) == 0:
        raise HTTPException(404, "No hay estudiantes")
    
    return listaEstudiantes


# READ - Obtener el estudiante filtrado por cedula
@router.get("/cedula/{cedula}", response_model=Estudiante)
async def estudiantePorCedula(cedula: str, session: SessionDep):

    """
    Obtener un estudiante por su cédula.

    Args:
        cedula (str): Cédula del estudiante.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Estudiante: El estudiante encontrado.

    Raises:
        HTTPException: 400 si la cédula no es numérica, 404 si no existe.
    """

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
    
    return estudianteDB



# READ - Obtener el estudiante filtrado por email
@router.get("/email/{email}", response_model=Estudiante)
async def estudiantePorCedula(email: str, session: SessionDep):

    """
    Obtener un estudiante por su email.

    Args:
        email (str): Email del estudiante.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Estudiante: El estudiante encontrado.

    Raises:
        HTTPException: 404 si no existe.
    """

    # Convertir el nombre a mayusculas
    email = email.lower()

    # Validar que el correo sea @ucatolica.edu.co
    if "@ucatolica.edu.co" not in email:
        raise HTTPException(400, "El email debe tener dominio ucatolica.edu.co")

    # Validar si existe el email
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.email == email)).first()
    # Si no existe el estudiante con ese email
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
    return estudianteDB



# READ - Obtener lista de estudiantes filtrados por semestre
@router.get("/semestre/{semestre}", response_model=list[Estudiante])
async def estudiantesPorSemestre(semestre: Semestre, session: SessionDep):

    """
    Obtener estudiantes filtrados por semestre.

    Args:
        semestre (Semestre): Semestre académico.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Estudiante]: Estudiantes en el semestre indicado.

    Raises:
        HTTPException: 404 si no hay estudiantes en ese semestre.
    """

    listaEstudiantes = session.exec(select(Estudiante).where(Estudiante.semestre == semestre)).all()
    # Si no hay estudiantes en ese semestre
    if len(listaEstudiantes) == 0:
        raise HTTPException(404, "No hay estudiantes en ese semestre")
    
    return listaEstudiantes



# READ - Obtener el curso filtrado por nombre
@router.get("/nombre/{nombre}", response_model=Estudiante)
async def estudiantesPorNombre(nombre: str, session: SessionDep):

    """
    Obtener un estudiante por su nombre exacto.

    Args:
        nombre (str): Nombre del estudiante (puede venir con %20 como espacios).
        session (SessionDep): Sesión de base de datos.

    Returns:
        Estudiante: El estudiante encontrado.

    Raises:
        HTTPException: 404 si no existe.
    """

    # Convertir el nombre a mayuscula y colocar espacios
    nombre = nombre.replace("%20", " ").upper()

    # Validar si existe el nombre
    estudianteDB = session.exec(select(Estudiante).where(Estudiante.nombre == nombre)).first()
    # Si no existe el estudiante con ese nombre
    if not estudianteDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
    return estudianteDB



# READ - Cursos de un estudiante
@router.get("/{cedula}/mis-cursos", response_model=list[Curso])
async def misCursos(cedula: str, session: SessionDep):

    """
    Obtener todos los cursos en los que está matriculado un estudiante.

    Args:
        cedula (str): Cédula del estudiante.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Curso]: Cursos matriculados por el estudiante.

    Raises:
        HTTPException: 400 si la cédula no es válida, 404 si no tiene cursos.
    """

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

    listaMisCursos = session.exec(
        select(Curso)
            .join(Matricula, Matricula.codigo == Curso.codigo)
            .where(Matricula.cedula == cedula,
                   or_(
                       Matricula.matriculado == EstadoMatricula.MATRICULADO,
                       Matricula.matriculado == EstadoMatricula.FINALIZADO
                   )
            )
        ).all()
    # Si el estudiante no tiene cursos
    if len(listaMisCursos) == 0:
        raise HTTPException(404, "No tienes cursos")
    
    return listaMisCursos



# READ - Obtener un estudiante filtrado por semestre y email
@router.get("/{semestre}/{email}", response_model=Estudiante)
async def estudiantePorSemestreYemail(semestre: Semestre, email: str, session: SessionDep):

    """
    Obtener un estudiante por semestre y email.

    Args:
        semestre (Semestre): Semestre académico.
        email (str): Email del estudiante.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Estudiante: El estudiante encontrado.

    Raises:
        HTTPException: 404 si no se encuentra o no coincide el semestre.
    """

    # Convertir el nombre a mayusculas
    email = email.lower()

    # Validar que el correo sea @ucatolica.edu.co
    if "@ucatolica.edu.co" not in email:
        raise HTTPException(400, "El email debe tener dominio ucatolica.edu.co")

    estudianteDB = session.exec(select(Estudiante).where(Estudiante.semestre == semestre or Estudiante.email == email)).first()
    # Si no existe un estudiante con ese email
    if not estudianteDB:
        raise HTTPException(404, f"Estudiante no encontrado")
    # Si el estudiante no esta en el semestre ingresado
    if estudianteDB.semestre != semestre:
        raise HTTPException(404, f"Estudiante con email {email} no esta en el semestre {semestre.value}")
    
    return estudianteDB



# UPDATE - Actualizar el semestre de un estudiante
@router.patch("/{cedula}/actualizar", response_model=Estudiante)
async def actualizarJornadaCurso(session: SessionDep, cedula: str, semestre: Semestre = Form(...)):

    """
    Actualizar el semestre de un estudiante.

    Args:
        session (SessionDep): Sesión de base de datos.
        cedula (str): Cédula del estudiante.
        semestre (Semestre): Nuevo semestre a asignar.

    Returns:
        Estudiante: Estudiante con el semestre actualizado.

    Raises:
        HTTPException: 400 si la cédula no es válida, 404 si no existe.
    """

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

    """
    Eliminar un estudiante y mover su información al histórico.

    También guarda en el histórico las matrículas asociadas con razón de eliminación.

    Args:
        cedula (str): Cédula del estudiante a eliminar.
        session (SessionDep): Sesión de base de datos.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException: 400 si la cédula no es válida, 404 si no existe.
    """

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
    
    # Guardar matrículas relacionadas en el histórico antes de borrar
    matriculasDB = session.exec(select(Matricula).where(Matricula.cedula == cedula)).all()
    for matricula in matriculasDB:
        # Determinar razón de eliminación según estado de la matricula
        if matricula.matriculado == EstadoMatricula.FINALIZADO:
            razon = "Curso finalizado - estudiante eliminado"
        elif matricula.matriculado == EstadoMatricula.DESMATRICULADO:
            razon = "Curso desmatriculado - estudiante eliminado"
        elif matricula.matriculado == EstadoMatricula.MATRICULADO:
            razon = "Curso en progreso - estudiante eliminado"
        else:
            razon = "Estado desconocido - estudiante eliminado"

        matriculaHistorica = MatriculaHistorica(
            codigo=matricula.codigo,
            cedula=matricula.cedula,
            matriculado=matricula.matriculado,
            razonEliminado=razon
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