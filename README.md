<div align="center">
  <h1>🎓 Sistema de Gestión de Universidad</h1>
  <p><em>Josué Ribero Duarte - 67001295</em></p>
  <p>
  Este proyecto implementa un sistema REST API desarrollado en FastAPI para gestionar estudiantes, cursos y matrículas de una universidad. 
  
  Permite realizar operaciones CRUD completas sobre estudiantes y cursos, además de manejar las relaciones **N:M** mediante el modelo de matrícula.
  </p>

  [![Version](https://img.shields.io/badge/Version-0.0.1-blue.svg)](https://github.com/tu-usuario/meraki/releases)
  [![FastAPI](https://img.shields.io/badge/FastAPI-v0.118.3-green.svg)](https://github.com/tu-usuario/meraki/releases)
  [![SQLModel](https://img.shields.io/badge/SQLModel-v0.0.24-green.svg)](https://github.com/tu-usuario/meraki/releases)
  [![Python](https://img.shields.io/badge/Python-3.13.5-yellow.svg)](https://github.com/tu-usuario/meraki/releases)
  [![SQLModel](https://img.shields.io/badge/SQLite-v3.51.0-orange.svg)](https://github.com/tu-usuario/meraki/releases)

</div>

***

## Requisitos y Lógica de Negocio

El sistema se diseñó para cumplir con los siguientes requisitos funcionales y reglas de negocio:

### Entidades y Relaciones

* **Curso** (`N`): Un curso puede tener muchos estudiantes.
* **Estudiante** (`N`): Un estudiante puede estar en muchos cursos (históricamente).
* **Matrícula** (`N:M`): Representa la inscripción de un estudiante en un curso.

### Reglas Clave

1.  **Código de Curso Único**: No se puede registrar un curso con un código que ya exista.
2.  **Matrícula Activa Única**: Un estudiante **no puede** estar registrado como **MATRICULADO (activo)** en más de un curso a la vez.
3.  **Gestión de Datos Históricos (Cascada)**:
    * Al **eliminar** un `Estudiante`, todas sus `Matrículas` asociadas se mueven a una tabla de **Histórico** antes de ser eliminadas de la tabla principal.
    * Al **eliminar** un `Curso`, todas las `Matrículas` asociadas a ese curso se mueven a una tabla de **Histórico** antes de ser eliminadas.

***

## Endpoints de la API (CRUD)

Los *endpoints* se agrupan por entidad y ofrecen las operaciones básicas de gestión y consulta:

### 1. Cursos (`/curso`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/crear` | Crea un nuevo curso. |
| `GET` | `/todos` | Lista todos los cursos. |
| `GET` | `/codigo/{codigo}` | Obtiene curso por código. |
| `GET` | `/nombre/{nombre}` | Obtiene curso por nombre. |
| `GET` | `/creditos/{creditos}` | Lista cursos filtrados por cantidad de créditos. |
| `GET` | `/horario/{horario}` | Lista cursos filtrados por horario. |
| `GET` | `/{codigo}/estudiantes` | **Lista estudiantes matriculados** en un curso. |
| `PATCH` | `/{codigo}/actualizar` | Actualiza el horario de un curso. |
| `DELETE` | `/{codigo}/eliminar` | Elimina un curso (con lógica de cascada a histórico de matrículas). |

### 2. Estudiantes (`/estudiante`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/crear` | Crea un nuevo estudiante. |
| `GET` | `/todos` | Lista todos los estudiantes. |
| `GET` | `/cedula/{cedula}` | Obtiene estudiante por cédula. |
| `GET` | `/email/{email}` | Obtiene estudiante por email. |
| `GET` | `/semestre/{semestre}` | Lista estudiantes filtrados por semestre. |
| `GET` | `/{cedula}/mis-cursos` | **Lista los cursos** en los que está matriculado/finalizado. |
| `PATCH` | `/{cedula}/actualizar` | Actualiza el semestre del estudiante. |
| `DELETE` | `/{cedula}/eliminar` | Elimina un estudiante (con lógica de cascada a histórico de matrículas). |

### 3. Matrículas (`/matricula`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/matricular-estudiante` | Matricula un estudiante en un curso (Valida restricción activa única). |
| `GET` | `/todos` | Lista todas las matrículas activas (`MATRICULADO`). |
| `GET` | `/estudiante/{cedula}` | Obtiene todas las matrículas (activas, finalizadas, desmatriculadas) de un estudiante. |
| `GET` | `/curso/{codigo}` | Obtiene las matrículas activas en un curso. |
| `PATCH` | `/{cedula}/finalizar` | Cambia el estado de la matrícula a **FINALIZADO**. |
| `PATCH` | `/{cedula}/rematricular` | Vuelve a activar una matrícula que estaba **DESMATRICULADA**. |
| `DELETE` | `/{cedula}/desmatricular` | Cambia el estado de la matrícula a **DESMATRICULADO**. |

***

## Estructura del Proyecto

El proyecto se organiza lógicamente por responsabilidades:

```
parcial_universidad/
│
├── 📄 main.py                          # Aplicación principal FastAPI
├── 📄 requirements.txt                  # Dependencias del proyecto
├── 📄 .gitignore                        # Archivos ignorados por Git
├── 📄 README.md                         # Este archivo
│
├── 📂 db/                               # Capa de datos
│   └── 📄 db.py                        # Configuración de SQLite y sesiones
│
├── 📂 models/                           # Modelos de datos (SQLModel)
│   ├── 📄 __init__.py
│   ├── 📄 curso.py                     # Modelo Curso + Histórico
│   ├── 📄 estudiante.py                # Modelo Estudiante + Histórico
│   └── 📄 matricula.py                 # Modelo Matrícula + Histórico
│
├── 📂 routers/                          # Endpoints de la API
│   ├── 📄 __init__.py
│   ├── 📄 curso_router.py              # CRUD de cursos
│   ├── 📄 estudiante_router.py         # CRUD de estudiantes
│   └── 📄 matricula_router.py          # CRUD de matrículas
│
├── 📂 utils/                            # Utilidades y helpers
│   ├── 📄 __init__.py
│   └── 📄 enum.py                      # Enumeraciones del sistema
│
├── 📂 documentacion/                    # Documentación del proyecto
│   ├── 📄 modelado.pdf
│   ├── 📄 requerimientos.pdf
│   └── 📄 mapa_endpoints.pdf
│
└── 📄 parcial_universidad.sqlite3       # Base de datos SQLite (generada)
```

***

## Cómo Empezar 🚀

### Requisitos Previos
* Tener **Git** instalado y configurado en tu sistema.
* Tener **Python 3.8+** instalado.

### Pasos de Instalación y Ejecución

1.  **Clonar el repositorio:**
    Abre tu terminal y ejecuta el comando:
    ```bash
    git clone https://github.com/Josue-Ribero/parcial_universidad.git
    ```

2.  **Crear un entorno virtual:**
    El comando que debes ejecutar es:
    ```bash
    python3 -m venv entorno # En Mac/Linux
    python -m venv entorno # En Windows
    ```

3.  **Activar entorno virtual:**
    El comando que debes ejecutar es:
    ```bash
    source entorno/bin/activate # En Mac/Linux
    entorno\Scripts\activate # En Windows
    ```

4.  **Instalar dependencias** (El `requirements.txt` contiene `fastapi`, `uvicorn`, `sqlmodel`, etc.).
    El comando que debes ejecutar es:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Crear archivo de configuración de Base de Datos (`db/db.py`):**
    Crea la carpeta `db` si no existe. Dentro de ella, crea el archivo `db.py` y pega el siguiente contenido para configurar la conexión a SQLite y las sesiones:
    ```python
    from fastapi import FastAPI, Depends
    from typing import Annotated
    from sqlmodel import SQLModel, Session, create_engine

    db_name = "parcial_universidad.sqlite3"
    db_url = f"sqlite:///{db_name}"
    engine = create_engine(db_url)

    def createAllTables(app: FastAPI):
        SQLModel.metadata.create_all(engine)
        yield

    def getSession():
        with Session(engine) as session:
            yield session

    SessionDep = Annotated[Session, Depends(getSession)]
    ```

6.  **Ejecutar el servidor**:
    Este es el comando que debes usar para iniciar la aplicación:
    ```bash
    fastapi dev
    ```

7.  Accede a la documentación interactiva (Swagger UI): **http://127.0.0.1:8000/docs**