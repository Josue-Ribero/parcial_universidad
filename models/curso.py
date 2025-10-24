from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..utils.enum import CreditosCurso, JornadaCurso

# Modelo base de curso
class CursoBase(SQLModel):
    codigo: Optional[str] = Field(default=None)
    nombre: Optional[str] = Field(default=None)
    creditos: CreditosCurso = Field(default=CreditosCurso.DOS)
    jornada: JornadaCurso = Field(default=JornadaCurso.DIURNA)

class Curso(CursoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    matriculaID: Optional[int] = Field(foreign_key="matricula.id")
    matriculas: list["Matricula"] = Relationship(back_populates="curso", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class CursoCreate(CursoBase):
    pass

class CursoCreate(CursoBase):
    pass

class CursoCreate(CursoBase):
    pass

# Importaciones diferidas
from .matricula import Matricula