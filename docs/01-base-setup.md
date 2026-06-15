# Rama 1: Base Setup — Estructura del Proyecto y Conexión a MySQL

## ¿Qué vamos a hacer?

En esta primera rama vamos a **sentar las bases** de nuestro proyecto. Antes de escribir cualquier endpoint o lógica de negocio, necesitamos:

1. Definir las **dependencias** (librerías que vamos a usar).
2. Configurar las **variables de entorno** (datos sensibles que no van en el código).
3. Conectarnos a **MySQL** usando un ORM (SQLAlchemy).
4. Crear la **estructura de carpetas** que seguirá la arquitectura en capas.
5. Configurar el **entry point** de nuestra aplicación FastAPI.

Piensen en esto como los **cimientos de una casa**: si los cimientos están bien, todo lo demás se construye fácil. Si están mal... bueno, ya se imaginan.

---

## Estructura de carpetas

```
myBackendProject/
├── main.py                  ← Entry point (aquí arranca todo)
├── requirements.txt         ← Dependencias del proyecto
├── .env.example             ← Template de variables de entorno
├── .gitignore               ← Archivos que Git debe ignorar
├── config/                  ← Configuración general
│   ├── __init__.py
│   ├── settings.py          ← Variables de configuración
│   └── database.py          ← Conexión a MySQL
├── models/                  ← Modelos de la base de datos (Persistencia)
│   └── __init__.py
├── repositories/            ← Acceso a datos (queries)
│   └── __init__.py
├── services/                ← Lógica de negocio
│   └── __init__.py
├── controllers/             ← Endpoints REST (controladores)
│   └── __init__.py
├── schemas/                 ← Validación de datos (DTOs)
│   └── __init__.py
├── utils/                   ← Utilidades transversales
│   └── __init__.py
└── middleware/              ← Middleware (manejo de errores, etc.)
    └── __init__.py
```

### ¿Por qué tantas carpetas vacías?

Cada carpeta representa una **capa** de nuestra arquitectura. Por ahora están vacías (solo tienen `__init__.py`), pero las iremos llenando en las siguientes ramas. Los archivos `__init__.py` le dicen a Python: *"esta carpeta es un paquete, puedes importar cosas desde aquí"*.

---

## Archivo por archivo

### 1. `requirements.txt` — Las dependencias

```txt
fastapi==0.115.0
uvicorn==0.30.6
sqlalchemy==2.0.35
pymysql==1.1.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
```

Vamos línea por línea:

| Librería | ¿Para qué sirve? |
|----------|-------------------|
| `fastapi` | El framework web. Es el que nos permite crear endpoints REST. |
| `uvicorn` | El servidor ASGI que ejecuta nuestra app FastAPI. Piensen en él como el "motor" que hace correr la app. |
| `sqlalchemy` | El ORM (Object-Relational Mapping). Nos permite interactuar con MySQL usando clases de Python en vez de escribir SQL crudo. |
| `pymysql` | El driver que SQLAlchemy usa para conectarse a MySQL. Es el "puente" entre Python y MySQL. |
| `python-jose` | Para crear y verificar tokens JWT (lo usaremos en la rama de login). |
| `passlib[bcrypt]` | Para hashear contraseñas de forma segura (lo usaremos en la rama de register). |
| `python-dotenv` | Para leer variables de entorno desde un archivo `.env`. |

**¿Por qué fijamos las versiones?** (el `==0.115.0`)

Porque si no, pip instala la última versión disponible. Si mañana sale una versión nueva con cambios que rompen algo, nuestro proyecto dejaría de funcionar. Fijar versiones = proyecto reproducible.

Para instalar todo:
```bash
pip install -r requirements.txt
```

---

### 2. `.env.example` — Template de variables de entorno

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/mybackendproject
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**¿Por qué un archivo `.env`?**

Porque hay datos que **nunca** deben estar en el código fuente:
- La contraseña de la base de datos.
- La clave secreta para firmar tokens.
- Credenciales de servicios externos.

Si suben eso a GitHub, cualquiera puede verlo. El `.env` se queda **solo en tu máquina** (está en el `.gitignore`). El `.env.example` es el **template** que sí sube al repo, para que tu compañero sepa qué variables necesita configurar.

**Desglose del `DATABASE_URL`:**
```
mysql+pymysql://root:password@localhost:3306/mybackendproject
│      │        │    │         │         │    │
│      │        │    │         │         │    └── nombre de la BD
│      │        │    │         │         └── puerto de MySQL
│      │        │    │         └── host (localhost = tu máquina)
│      │        │    └── contraseña del usuario
│      │        └── usuario de MySQL
│      └── driver (pymysql)
└── tipo de base de datos (mysql)
```

---

### 3. `config/settings.py` — Variables de configuración

```python
import os                          # Línea 1
from dotenv import load_dotenv     # Línea 2

load_dotenv()                      # Línea 4

DATABASE_URL: str = os.getenv(     # Línea 6-9
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/mybackendproject"
)

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")  # Línea 11
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")                                   # Línea 12
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # Línea 13
```

**Explicación línea por línea:**

- **Línea 1**: `import os` — módulo estándar de Python para interactuar con el sistema operativo. Lo usamos para leer variables de entorno.

- **Línea 2**: `from dotenv import load_dotenv` — importamos la función que lee el archivo `.env` y carga sus valores como variables de entorno.

- **Línea 4**: `load_dotenv()` — ejecutamos la carga. Después de esta línea, todo lo que está en `.env` ya es accesible con `os.getenv()`.

- **Líneas 6-9**: `os.getenv("DATABASE_URL", "valor_por_defecto")` — busca la variable `DATABASE_URL` en el entorno. Si no la encuentra (porque no hay `.env`), usa el valor por defecto. El type hint `: str` es para que el IDE sepa que es un string.

- **Línea 13**: Fíjense que hacemos `int(os.getenv(...))` — porque las variables de entorno **siempre son strings**. Si necesitamos un número, hay que convertirlo.

**¿Por qué un archivo de settings y no leer `.env` directamente en cada archivo?**

Porque si mañana cambiamos cómo leemos la configuración (por ejemplo, de `.env` a un servicio de secretos como AWS Secrets Manager), solo cambiamos **este archivo**. El resto del proyecto sigue importando desde `config.settings` sin enterarse del cambio. Eso es el principio de **responsabilidad única**.

---

### 4. `config/database.py` — Conexión a MySQL

```python
from sqlalchemy import create_engine                     # Línea 1
from sqlalchemy.orm import sessionmaker, DeclarativeBase  # Línea 2

from config.settings import DATABASE_URL                  # Línea 4

engine = create_engine(DATABASE_URL, echo=True)           # Línea 6

SessionLocal = sessionmaker(                              # Línea 8
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):                              # Línea 14
    pass


def get_db():                                             # Línea 18
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Este es el archivo más importante de esta rama.** Vamos pieza por pieza:

#### `engine` (Línea 6)
```python
engine = create_engine(DATABASE_URL, echo=True)
```
El **engine** es la conexión a MySQL. `create_engine` recibe la URL de conexión y crea un pool de conexiones (no abre una conexión por cada query, las reutiliza). El `echo=True` imprime las queries SQL en consola — útil para aprender, se quita en producción.

#### `SessionLocal` (Líneas 8-12)
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
Una **Session** es como una "conversación" con la base de datos. Cada vez que queremos hacer queries, abrimos una sesión, hacemos lo que necesitamos, y la cerramos.

- `autocommit=False` → nosotros decidimos cuándo guardar los cambios (con `db.commit()`).
- `autoflush=False` → los cambios no se envían automáticamente a la BD.
- `bind=engine` → esta sesión usa nuestra conexión a MySQL.

#### `Base` (Líneas 14-15)
```python
class Base(DeclarativeBase):
    pass
```
**Base** es la clase padre de todos nuestros modelos. Cuando creemos el modelo `User` o `Task`, van a heredar de `Base`. SQLAlchemy usa esto para saber qué tablas crear en la base de datos.

#### `get_db()` (Líneas 18-23)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
Esta es una **dependency** de FastAPI. Es una función generadora (usa `yield` en vez de `return`). Funciona así:

1. Cuando un endpoint necesita la BD, FastAPI llama a `get_db()`.
2. Se crea una sesión (`SessionLocal()`).
3. Se le **entrega** al endpoint (`yield db`).
4. El endpoint hace su trabajo.
5. **Siempre** se cierra la sesión (`finally: db.close()`), haya error o no.

Esto es el patrón **Dependency Injection**: el endpoint no crea su propia conexión a la BD, se la **inyectan**. ¿Por qué? Porque si mañana cambiamos la BD de MySQL a PostgreSQL, solo cambiamos este archivo. Los endpoints ni se enteran.

---

### 5. `main.py` — El entry point

```python
from contextlib import asynccontextmanager               # Línea 1

from fastapi import FastAPI                               # Línea 3

from config.database import Base, engine                  # Línea 5


@asynccontextmanager                                      # Línea 8
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(                                            # Línea 13
    title="Mi Backend Project",
    description="Proyecto educativo - Arquitectura en Capas",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")                                             # Línea 21
async def bienvenida():
    return {"mensaje": "¡Bienvenido a Mi Backend Project!"}
```

#### `lifespan` (Líneas 8-11)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
```
El **lifespan** es código que se ejecuta **al arrancar** la aplicación (antes de recibir requests) y **al apagarla**.

- `Base.metadata.create_all(bind=engine)` → revisa todos los modelos que heredan de `Base` y crea sus tablas en MySQL **si no existen**. No borra datos existentes.
- `yield` → aquí la app empieza a recibir requests. Todo lo que pongas después del `yield` se ejecuta al apagar la app.

#### `app = FastAPI(...)` (Líneas 13-18)
Creamos la instancia de FastAPI con metadatos que aparecen en la documentación automática de Swagger (`/docs`).

El parámetro `lifespan=lifespan` conecta nuestro ciclo de vida con la app.

#### Endpoint raíz (Líneas 21-23)
Un endpoint simple de prueba. Si hacemos `GET /` nos devuelve un JSON de bienvenida. Lo usamos para verificar que la app arranca.

---

### 6. `.gitignore` — Lo que Git debe ignorar

```gitignore
__pycache__/
*.pyc
venv/
.env
```

| Patrón | ¿Qué ignora? |
|--------|---------------|
| `__pycache__/` | Archivos compilados de Python (se generan automáticamente) |
| `*.pyc` | Archivos bytecode de Python |
| `venv/` | El entorno virtual (cada developer crea el suyo) |
| `.env` | Variables de entorno con datos sensibles |

**Regla de oro:** si el archivo se genera automáticamente, contiene datos sensibles, o es específico de tu máquina → va en `.gitignore`.

---

## ¿Cómo verifico que funciona?

### 1. Crear la base de datos en MySQL
```sql
CREATE DATABASE mybackendproject;
```

### 2. Crear el archivo `.env`
```bash
cp .env.example .env
# Editar .env con tus credenciales reales de MySQL
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Arrancar la app
```bash
uvicorn main:app --reload
```

### 5. Verificar
- Abrir http://localhost:8000 → debe mostrar `{"mensaje": "¡Bienvenido a Mi Backend Project!"}`
- Abrir http://localhost:8000/docs → debe cargar la documentación Swagger

Si ven en la consola las queries SQL (gracias al `echo=True`), significa que la conexión a MySQL está funcionando.

---

## Diagrama de lo que construimos

```
                    ┌─────────────┐
                    │   main.py   │ ← Entry point
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │ usa
                    ┌──────▼──────┐
                    │   config/   │
                    ├─────────────┤
                    │ settings.py │ ← Lee .env
                    │ database.py │ ← Conexión MySQL
                    └──────┬──────┘
                           │ conecta
                    ┌──────▼──────┐
                    │    MySQL    │
                    │    (BD)     │
                    └─────────────┘
```

---

## Conceptos clave de esta rama

| Concepto | ¿Qué es? | ¿Dónde lo vimos? |
|----------|-----------|-------------------|
| ORM | Mapear clases de Python a tablas de BD | `database.py` (SQLAlchemy) |
| Dependency Injection | Inyectar dependencias en vez de crearlas | `get_db()` |
| Lifespan | Código que corre al iniciar/apagar la app | `main.py` |
| Variables de entorno | Configuración sensible fuera del código | `settings.py` + `.env` |
| Paquetes Python | Carpetas con `__init__.py` que permiten imports | Todas las carpetas |

---

## ¿Qué sigue?

En la siguiente rama (`feature/register`) vamos a crear nuestro **primer flujo completo** a través de todas las capas: el registro de usuarios. Ahí van a ver cómo el modelo, el repository, el service y el controller trabajan juntos.
