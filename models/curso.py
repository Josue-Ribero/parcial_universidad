from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime as dt
from typing import Optional
from ..utils.enum import CreditosCurso, HorarioCurso

# Modelo base de curso
class CursoBase(SQLModel):
    codigo: Optional[str] = Field(default=None, min_length=7, max_length=7)
    nombre: Optional[str] = Field(default=None)
    creditos: CreditosCurso = Field(default=CreditosCurso.DOS)
    horario: HorarioCurso = Field(default=HorarioCurso.SIETE_A_NUEVE)

class Curso(CursoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    matriculas: list["Matricula"] = Relationship(back_populates="curso", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class CursoUpdate(CursoBase):
    pass

class CursoDelete(CursoBase):
    pass

class CursoHistorico(SQLModel, table=True):
    id: int = Field(primary_key=True)
    codigo: str
    nombre: str
    creditos: CreditosCurso
    horario: HorarioCurso
    fechaEliminado: dt = Field(default_factory=dt.now)

# Importaciones diferidas
from .matricula import Matricula