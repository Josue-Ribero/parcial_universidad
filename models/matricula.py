from datetime import datetime as dt
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..utils.enum import EstadoMatricula

# Modelo base de Matricula
class MatriculaBase(SQLModel):
    fecha: dt = Field(default_factory=dt.now)
    matriculado: EstadoMatricula = Field(default=EstadoMatricula.MATRICULADO)

class Matricula(MatriculaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cursoID: Optional[int] = Field(foreign_key="curso.id")
    curso: Optional["Curso"] = Relationship(back_populates="matriculas")
    estudianteID: Optional[int] = Field(foreign_key="estudiante.id", ondelete="CASCADE")
    estudiante: Optional["Estudiante"] = Relationship(back_populates="matriculas")

class MatriculaCreate(MatriculaBase):
    pass

class MatriculaCreate(MatriculaBase):
    pass

class MatriculaCreate(MatriculaBase):
    pass

# Importaciones diferidas
from .curso import Curso
from .estudiante import Estudiante