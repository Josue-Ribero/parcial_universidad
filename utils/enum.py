# Importacion de Enum
from enum import Enum

# ENUMERACIONES CURSOS

# Cantidad de creditos de un curso
class CreditosCurso(Enum):
    UNO = "1"
    DOS = "2"
    TRES = "3"
    CUATRO = "4"

# Horarios cursos
class HorarioCurso(Enum):
    SIETE_A_NUEVE = "SIETE_A_NUEVE"
    NUEVE_A_ONCE = "NUEVE_A_ONCE"
    ONCE_A_UNA = "ONCE_A_UNA"
    DOS_A_CUATRO = "DOS_A_CUATRO"
    CUATRO_A_SEIS = "CUATRO_A_SEIS"
    SEIS_A_OCHO = "SEIS_A_OCHO"


# ENUMERACIONES ESTUDIANTES

# Semestre que esta cursando el estudiante
class Semestre(Enum):
    PRIMERO = "1"
    SEGUNDO = "2"
    TERCERO = "3"
    CUARTO = "4"
    QUINTO = "5"
    SEXTO = "6"
    SEPTIMO = "7"
    OCTAVO = "8"
    NOVENO = "9"
    DECIMO = "10"
    UNDECIMO = "11"
    DUODECIMO = "12"


# ENUMERACIONES MATRICULAS
class EstadoMatricula(Enum):
    MATRICULADO = "MATRICULADO"
    DESMATRICULADO = "DESMATRICULADO"