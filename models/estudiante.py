from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from ..utils.enum import Semestre

# Modelo base de Estudiante
class EstudianteBase(SQLModel):
    cedula: Optional[str] = Field(default=None, unique=True)
    nombre: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None, unique=True)
    semestre: Semestre = Field(default=Semestre.PRIMERO)

class Estudiante(EstudianteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    matriculas: list["Matricula"] = Relationship(back_populates="estudiante", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class EstudianteUpdate(EstudianteBase):
    pass

class EstudianteDelete(EstudianteBase):
    pass

# Importaciones diferidas
from .matricula import Matricula