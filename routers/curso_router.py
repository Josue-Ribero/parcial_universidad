"""
Módulo: curso_router
--------------------
Endpoints relacionados con la gestión de cursos en el sistema académico.

Incluye operaciones para crear, consultar, actualizar y eliminar cursos, así como
la consulta de estudiantes matriculados en un curso específico.
"""

from fastapi import APIRouter, HTTPException, Form
from ..db.db import SessionDep
from sqlmodel import select
from ..models.curso import Curso, CursoHistorico
from ..models.matricula import Matricula, MatriculaHistorica
from ..models.estudiante import Estudiante
from ..utils.enum import CreditosCurso, HorarioCurso

router = APIRouter(prefix="/curso", tags=["Cursos"])

# CREATE - Crear curso
@router.post("/crear", response_model=Curso, status_code=201)
async def crearCurso(
    session: SessionDep,
    codigo: str = Form(...),
    nombre: str = Form(...),
    creditos: CreditosCurso = Form(...),
    horario: HorarioCurso = Form(...)
    ):

    """
    Crear un nuevo curso.

    Valida que el código no exista previamente y que tenga exactamente 7 caracteres.
    Convierte código y nombre a mayúsculas antes de almacenarlos.

    Args:
        session (SessionDep): Sesión de base de datos.
        codigo (str): Código único del curso (7 caracteres).
        nombre (str): Nombre completo del curso.
        creditos (CreditosCurso): Número de créditos académicos.
        horario (HorarioCurso): Horario asignado al curso.

    Returns:
        Curso: El curso creado.

    Raises:
        HTTPException: 400 si el código ya existe o no tiene 7 caracteres.
    """

    # Validar si el curso ya existe
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    if cursoDB:
        raise HTTPException(400, "Ya hay un curso registrado con ese codigo")
    
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Convertir el nombre a mayusculas
    nombre = nombre.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    # Si no existe, lo crea
    nuevoCurso = Curso(
        codigo=codigo,
        nombre=nombre,
        creditos=creditos,
        horario=horario
    )
    # Insertar el curso a la DB
    session.add(nuevoCurso)
    session.commit() # Guardar los cambios
    session.refresh(nuevoCurso)

    return nuevoCurso # Devuelve el objeto curso



# READ - Obtener todos los cursos que hay
@router.get("/todos", response_model=list[Curso])
async def listaCursos(session: SessionDep):

    """
    Obtener todos los cursos registrados.

    Args:
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Curso]: Lista de todos los cursos.

    Raises:
        HTTPException: 404 si no hay cursos registrados.
    """

    listaCursos = session.exec(select(Curso)).all()
    # Si no hay cursos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos")
    
    return listaCursos



# READ - Obtener el curso filtrado por codigo
@router.get("/codigo/{codigo}", response_model=Curso)
async def cursosPorCodigo(codigo: str, session: SessionDep):

    """
    Obtener un curso por su código.

    Args:
        codigo (str): Código del curso en mayúsculas.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Curso: El curso encontrado.

    Raises:
        HTTPException: 404 si no existe un curso con ese código.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    # Validar si existe el codigo
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso con ese codigo
    if not cursoDB:
        raise HTTPException(404, "No existe ese curso")
    
    return cursoDB



# READ - Obtener el curso filtrado por nombre
@router.get("/nombre/{nombre}", response_model=Curso)
async def cursosPorNombre(nombre: str, session: SessionDep):

    """
    Obtener un curso por su nombre exacto.

    Args:
        nombre (str): Nombre del curso (puede venir con %20 como espacios).
        session (SessionDep): Sesión de base de datos.

    Returns:
        Curso: El curso encontrado.

    Raises:
        HTTPException: 404 si no existe un curso con ese nombre.
    """

    # Convertir el nombre a mayuscula y colocar espacios
    nombre = nombre.replace("%20", " ").upper()

    # Validar si existe el nombre
    cursoDB = session.exec(select(Curso).where(Curso.nombre == nombre)).first()
    # Si no existe el curso con ese nombre
    if not cursoDB:
        raise HTTPException(404, "No existe ese curso")
    
    return cursoDB


# READ - Obtener lista de cursos filtrados por creditos
@router.get("/creditos/{creditos}", response_model=list[Curso])
async def cursosPorCreditos(session: SessionDep, creditos: CreditosCurso):

    """
    Obtener cursos filtrados por cantidad de créditos.

    Args:
        creditos (CreditosCurso): Cantidad de créditos a filtrar.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Curso]: Cursos que tienen la cantidad de créditos especificada.

    Raises:
        HTTPException: 404 si no hay cursos con esa cantidad de créditos.
    """

    listaCursos = session.exec(select(Curso).where(Curso.creditos == creditos)).all()
    # Si no hay cursos con esos creditos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos con esa cantidad de creditos")
    
    return listaCursos



# READ - Obtener lista de cursos filtrados por horario
@router.get("/horario/{horario}", response_model=list[Curso])
async def cursosPorCreditos(session: SessionDep, horario: HorarioCurso):

    """
    Obtener cursos filtrados por horario.

    Args:
        horario (HorarioCurso): Horario a filtrar.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Curso]: Cursos que tienen el horario especificado.

    Raises:
        HTTPException: 404 si no hay cursos en ese horario.
    """

    listaCursos = session.exec(select(Curso).where(Curso.horario == horario)).all()
    # Si no hay cursos con esos creditos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos en ese horario")
    
    return listaCursos



# READ - Estudiantes matriculados en un curso
@router.get("/{codigo}/estudiantes", response_model=list[Estudiante])
async def estudiantesPorCurso(codigo: str, session: SessionDep):

    """
    Obtener todos los estudiantes matriculados en un curso.

    Args:
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        list[Estudiante]: Estudiantes matriculados en el curso.

    Raises:
        HTTPException: 404 si el curso no existe o no tiene estudiantes.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    # Validar si el codigo existe
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, "El curso no existe")

    estudiantesEnCurso = session.exec(select(Estudiante).join(Matricula, Matricula.cedula == Estudiante.cedula).where(Matricula.codigo == codigo)).all()
    # Si no hay estudiantes en ese curso
    if len(estudiantesEnCurso) == 0:
        raise HTTPException(404, "No hay estudiantes en ese curso")
    
    return estudiantesEnCurso



# READ - Obtener un curso filtrado por creditos y codigo
@router.get("/{creditos}/{codigo}", response_model=Curso)
async def cursoPorCreditosYcodigo(creditos: CreditosCurso, codigo: str, session: SessionDep):

    """
    Obtener un curso específico por créditos y código.

    Args:
        creditos (CreditosCurso): Cantidad de créditos.
        codigo (str): Código del curso.
        session (SessionDep): Sesión de base de datos.

    Returns:
        Curso: El curso que cumple ambas condiciones.

    Raises:
        HTTPException: 404 si no se encuentra o no coincide en créditos.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    cursoDB = session.exec(select(Curso).where(Curso.creditos == creditos or Curso.codigo == codigo)).first()
    # Si no existe un estudiante con ese email
    if not cursoDB:
        raise HTTPException(404, f"Curso no encontrado")
    # Si el estudiante no esta en el semestre ingresado
    if cursoDB.creditos != creditos:
        raise HTTPException(404, f"Curso con codigo {codigo} no tiene {creditos.value} creditos")
    
    return cursoDB



# UPDATE - Actualizar el horario de un curso
@router.patch("/{codigo}/actualizar", response_model=Curso)
async def actualizarHorarioCurso(session: SessionDep, codigo: str, horario: HorarioCurso = Form(...)):

    """
    Actualizar el horario de un curso.

    Args:
        session (SessionDep): Sesión de base de datos.
        codigo (str): Código del curso.
        horario (HorarioCurso): Nuevo horario a asignar.

    Returns:
        Curso: Curso con el horario actualizado.

    Raises:
        HTTPException: 404 si el curso no existe.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, "Curso no encontrado")
    
    # Validar si el curso ya esta en esa franja horaria
    if cursoDB.horario == horario:
        raise HTTPException(400, "El curso ya se encuentra en esa franja horaria")
    
    # Cambiar la horario del curso
    cursoDB.horario = horario
    #Insertar curso actualizado en la DB
    session.add(cursoDB)
    session.commit() # Guardar los cambios
    session.refresh(cursoDB)
    
    return cursoDB



# DELETE - Eliminar un curso
@router.delete("/{codigo}/eliminar")
async def eliminarCurso(codigo: str, session: SessionDep):

    """
    Eliminar un curso y mover su información al histórico.

    También guarda en el histórico las matrículas asociadas.

    Args:
        codigo (str): Código del curso a eliminar.
        session (SessionDep): Sesión de base de datos.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException: 404 si el curso no existe.
    """

    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar que el codigo sea valido
    if not len(codigo) == 7:
        raise HTTPException(400, "El codigo debe tener entre 7 caracteres")

    # Validar si ya existe el curso
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, "Estudiante no encontrado")
    
    # Guardar matrículas relacionadas en el histórico antes de borrar
    matriculasDB = session.exec(select(Matricula).where(Matricula.codigo == codigo)).all()
    for matricula in matriculasDB:
        matriculaHistorica = MatriculaHistorica(
            codigo=matricula.codigo,
            cedula=matricula.cedula,
            matriculado=matricula.matriculado,
            razonEliminado="Curso eliminado"
        )
        # Insertar las matriculas del curso al historico
        session.add(matriculaHistorica)
    session.commit() # Guardar los cambios
    
    # Copiar a curso historico
    cursoHistorico = CursoHistorico(
        codigo=cursoDB.codigo,
        nombre=cursoDB.nombre,
        creditos=cursoDB.creditos,
        horario=cursoDB.horario
    )
    session.add(cursoHistorico)
    
    # Eliminar el curso de la DB
    session.delete(cursoDB)
    session.commit() # Guardar los cambios

    return {"Mensaje": "Curso eliminado correctamente"}