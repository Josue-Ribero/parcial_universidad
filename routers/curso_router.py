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
    # Validar si el curso ya existe
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    if cursoDB:
        raise HTTPException(400, "Ya hay un curso registrado con ese codigo")
    
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
    listaCursos = session.exec(select(Curso)).all()
    # Si no hay cursos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos")
    
    return listaCursos



# READ - Obtener el curso filtrado por codigo
@router.get("/codigo/{codigo}", response_model=Curso)
async def cursosPorCodigo(codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

    # Validar si existe el codigo
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
@router.get("/{codigo}/estudiantes", response_model=list[Estudiante])
async def estudiantesPorCurso(codigo: str, session: SessionDep):
    # Convertir el codigo a mayuscula
    codigo = codigo.upper()

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



# READ - Obtener lista de cursos filtrados por horario
@router.get("/horario/{horario}", response_model=list[Curso])
async def cursosPorCreditos(session: SessionDep, horario: HorarioCurso):
    listaCursos = session.exec(select(Curso).where(Curso.horario == horario)).all()
    # Si no hay cursos con esos creditos
    if len(listaCursos) == 0:
        raise HTTPException(404, "No hay cursos en ese horario")
    
    return listaCursos



# UPDATE - Actualizar el horario de un curso
@router.patch("/{codigo}/actualizar", response_model=Curso)
async def actualizarHorarioCurso(session: SessionDep, codigo: str, horario: HorarioCurso = Form(...)):
    # Verificar que el curso exista
    cursoDB = session.exec(select(Curso).where(Curso.codigo == codigo)).first()
    # Si no existe el curso
    if not cursoDB:
        raise HTTPException(404, "Curso no encontrado")
    
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

    return {"Mensaje": "Estudiante eliminado correctamente"}