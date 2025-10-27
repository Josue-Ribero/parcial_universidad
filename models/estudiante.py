"""
Módulo: estudiante
------------------
Define los modelos relacionados con los estudiantes del sistema académico.

Incluye el modelo principal `Estudiante`, su versión histórica 
(`EstudianteHistorico`) y los modelos auxiliares para actualización y eliminación.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime as dt
from typing import Optional
from ..utils.enum import Semestre


class EstudianteBase(SQLModel):
    """
    Modelo base de estudiante.

    Define los campos comunes a todas las variantes del modelo `Estudiante`.

    Attributes:
        cedula (Optional[str]): Documento de identidad único del estudiante.
        nombre (Optional[str]): Nombre completo del estudiante.
        email (Optional[str]): Correo electrónico institucional o personal.
        semestre (Semestre): Nivel académico actual del estudiante.
    """
    cedula: Optional[str] = Field(default=None, unique=True, min_length=7, max_length=10)
    nombre: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None, unique=True)
    semestre: Semestre = Field(default=Semestre.PRIMERO)


class Estudiante(EstudianteBase, table=True):
    """
    Modelo de estudiante almacenado en la base de datos.

    Representa a un estudiante inscrito en la institución, con su información
    personal y relación con las matrículas activas.

    Attributes:
        id (Optional[int]): Identificador único del estudiante.
        matriculas (list[Matricula]): Lista de matrículas asociadas al estudiante.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    matriculas: list["Matricula"] = Relationship(
        back_populates="estudiante", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class EstudianteUpdate(EstudianteBase):
    """
    Modelo utilizado para la actualización de información de un estudiante.
    """
    pass


class EstudianteDelete(EstudianteBase):
    """
    Modelo auxiliar utilizado en la eliminación de registros de estudiantes.
    """
    pass


class EstudianteHistorico(SQLModel, table=True):
    """
    Registro histórico de los estudiantes eliminados.

    Permite mantener una copia de los datos de estudiantes que fueron
    removidos del sistema, junto con la fecha de eliminación.

    Attributes:
        id (int): Identificador del registro histórico.
        cedula (str): Cédula del estudiante eliminado.
        nombre (str): Nombre del estudiante eliminado.
        email (str): Correo electrónico del estudiante eliminado.
        semestre (Semestre): Semestre en el que estaba inscrito.
        fechaEliminado (datetime): Fecha de eliminación del registro.
    """
    id: int = Field(primary_key=True)
    cedula: str
    nombre: str
    email: str
    semestre: Semestre
    fechaEliminado: dt = Field(default_factory=dt.now)


# Importación diferida
from .matricula import Matricula