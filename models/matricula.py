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
    codigo: Optional[str] = Field(foreign_key="curso.codigo", ondelete="CASCADE")
    curso: Optional["Curso"] = Relationship(back_populates="matriculas")
    cedula: Optional[str] = Field(foreign_key="estudiante.cedula", ondelete="CASCADE")
    estudiante: Optional["Estudiante"] = Relationship(back_populates="matriculas")

class MatriculaUpdate(MatriculaBase):
    pass

class MatriculaDelete(MatriculaBase):
    pass

class MatriculaHistorica(SQLModel, table=True):
    id: int = Field(primary_key=True)
    codigo: str
    cedula: str
    matriculado: EstadoMatricula
    fechaEliminado: dt = Field(default_factory=dt.now)
    razonEliminado: Optional[str] = None

# Importaciones diferidas
from .curso import Curso
from .estudiante import Estudiante