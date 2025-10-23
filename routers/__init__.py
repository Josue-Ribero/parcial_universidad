from .curso_router import router as router_curso
from .estudiante_router import router as router_estudiante
from .matricula_router import router as router_matricula

__all__ = [
    "router_curso",
    "router_estudiante",
    "router_matricula"
]