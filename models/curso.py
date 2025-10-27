"""
Módulo: curso
-------------
Define los modelos relacionados con los cursos ofrecidos en el sistema académico.

Incluye el modelo principal `Curso`, su versión histórica (`CursoHistorico`) y 
los modelos auxiliares para operaciones de actualización y eliminación.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime as dt
from typing import Optional
from ..utils.enum import CreditosCurso, HorarioCurso


class CursoBase(SQLModel):
    """
    Modelo base de curso.

    Define los campos comunes a todas las variantes del modelo `Curso`.

    Attributes:
        codigo (Optional[str]): Código único del curso, debe tener exactamente 7 caracteres.
        nombre (Optional[str]): Nombre completo del curso.
        creditos (CreditosCurso): Cantidad de créditos académicos del curso.
        horario (HorarioCurso): Horario asignado al curso.
    """
    codigo: Optional[str] = Field(default=None, min_length=7, max_length=7)
    nombre: Optional[str] = Field(default=None)
    creditos: CreditosCurso = Field(default=CreditosCurso.DOS)
    horario: HorarioCurso = Field(default=HorarioCurso.SIETE_A_NUEVE)


class Curso(CursoBase, table=True):
    """
    Modelo de curso almacenado en la base de datos.

    Representa un curso académico con su respectiva información y relación 
    con las matrículas registradas.

    Attributes:
        id (Optional[int]): Identificador único del curso.
        matriculas (list[Matricula]): Lista de matrículas asociadas al curso.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    matriculas: list["Matricula"] = Relationship(
        back_populates="curso", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class CursoUpdate(CursoBase):
    """
    Modelo para la actualización de información de un curso existente.
    """
    pass


class CursoDelete(CursoBase):
    """
    Modelo auxiliar utilizado en la eliminación de cursos.
    """
    pass


class CursoHistorico(SQLModel, table=True):
    """
    Registro histórico de los cursos eliminados.

    Permite conservar un historial de los cursos que han sido removidos del sistema,
    con su información y la fecha de eliminación.

    Attributes:
        id (int): Identificador del registro histórico.
        codigo (str): Código del curso eliminado.
        nombre (str): Nombre del curso eliminado.
        creditos (CreditosCurso): Créditos del curso eliminado.
        horario (HorarioCurso): Horario del curso eliminado.
        fechaEliminado (datetime): Fecha en que el curso fue eliminado.
    """
    id: int = Field(primary_key=True)
    codigo: str
    nombre: str
    creditos: CreditosCurso
    horario: HorarioCurso
    fechaEliminado: dt = Field(default_factory=dt.now)


# Importación diferida para evitar referencias circulares
from .matricula import Matricula