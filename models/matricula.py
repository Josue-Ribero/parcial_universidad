"""
Módulo: matricula
-----------------
Define los modelos asociados al proceso de matrícula entre estudiantes y cursos.

Incluye el modelo principal `Matricula`, su versión histórica 
(`MatriculaHistorica`) y los modelos auxiliares para actualización y eliminación.
"""

from datetime import datetime as dt
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..utils.enum import EstadoMatricula


class MatriculaBase(SQLModel):
    """
    Modelo base de matrícula.

    Define los campos comunes de todas las variantes del modelo `Matricula`.

    Attributes:
        fecha (datetime): Fecha en la que se realizó la matrícula.
        matriculado (EstadoMatricula): Estado actual de la matrícula 
            (ejemplo: MATRICULADO, RETIRADO, FINALIZADO).
    """
    fecha: dt = Field(default_factory=dt.now)
    matriculado: EstadoMatricula = Field(default=EstadoMatricula.MATRICULADO)


class Matricula(MatriculaBase, table=True):
    """
    Modelo de matrícula almacenado en la base de datos.

    Representa la relación entre un estudiante y un curso específico.

    Attributes:
        id (Optional[int]): Identificador único de la matrícula.
        codigo (Optional[str]): Código del curso asociado.
        curso (Optional[Curso]): Relación con el curso matriculado.
        cedula (Optional[str]): Cédula del estudiante matriculado.
        estudiante (Optional[Estudiante]): Relación con el estudiante.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: Optional[str] = Field(foreign_key="curso.codigo", ondelete="CASCADE")
    curso: Optional["Curso"] = Relationship(back_populates="matriculas")
    cedula: Optional[str] = Field(foreign_key="estudiante.cedula", ondelete="CASCADE")
    estudiante: Optional["Estudiante"] = Relationship(back_populates="matriculas")


class MatriculaUpdate(MatriculaBase):
    """
    Modelo utilizado para la actualización de información de una matrícula.
    """
    pass


class MatriculaDelete(MatriculaBase):
    """
    Modelo auxiliar utilizado en la eliminación de registros de matrícula.
    """
    pass


class MatriculaHistorica(SQLModel, table=True):
    """
    Registro histórico de las matrículas eliminadas.

    Permite mantener un historial de las relaciones estudiante-curso que 
    han sido eliminadas, incluyendo la fecha y razón de eliminación.

    Attributes:
        id (int): Identificador del registro histórico.
        codigo (str): Código del curso asociado.
        cedula (str): Cédula del estudiante matriculado.
        matriculado (EstadoMatricula): Estado de la matrícula.
        fechaEliminado (datetime): Fecha en que se eliminó el registro.
        razonEliminado (Optional[str]): Motivo de la eliminación (si aplica).
    """
    id: int = Field(primary_key=True)
    codigo: str
    cedula: str
    matriculado: EstadoMatricula
    fechaEliminado: dt = Field(default_factory=dt.now)
    razonEliminado: Optional[str] = None


# Importaciones diferidas para evitar referencias circulares
from .curso import Curso
from .estudiante import Estudiante