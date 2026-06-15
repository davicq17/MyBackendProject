# Rama 2: Register — Registro de Usuarios

## ¿Qué vamos a hacer?

Vamos a implementar nuestro **primer flujo completo** a través de todas las capas de la arquitectura. Cuando un usuario haga `POST /auth/register`, el request va a atravesar:

```
Controller → Service → Repository → Base de Datos
```

Y la respuesta vuelve por el mismo camino. Esto es la esencia de la **arquitectura en capas**: cada capa tiene una responsabilidad clara y solo habla con la capa de al lado.

---

## ¿Qué archivos creamos?

| Archivo | Capa | Responsabilidad |
|---------|------|-----------------|
| `models/user_model.py` | Persistencia | Define la tabla `users` en MySQL |
| `schemas/user_schema.py` | Validación | Define qué datos entran y salen de la API |
| `utils/security.py` | Transversal | Hashear y verificar contraseñas |
| `repositories/user_repository.py` | Acceso a Datos | Queries a la tabla `users` |
| `services/auth_service.py` | Lógica de Negocio | Reglas de registro |
| `controllers/auth_controller.py` | Controlador | Endpoint `POST /auth/register` |

---

## Archivo por archivo

### 1. `models/user_model.py` — El modelo (Capa de Persistencia)

```python
from datetime import datetime                                    # Línea 1

from sqlalchemy import String, Boolean, DateTime, func           # Línea 3
from sqlalchemy.orm import Mapped, mapped_column                 # Línea 4

from config.database import Base                                 # Línea 6


class User(Base):                                                # Línea 9
    __tablename__ = "users"                                      # Línea 10

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)          # Línea 12
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)  # Línea 13
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)            # Línea 14
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)      # Línea 15
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)                 # Línea 16
    role: Mapped[str] = mapped_column(String(50), default="user")                  # Línea 17
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())  # Línea 18
```

**¿Qué es un modelo?**

Un modelo es una **clase de Python que representa una tabla** en la base de datos. Cada atributo de la clase es una columna de la tabla. SQLAlchemy se encarga de traducir esto a SQL.

**Línea por línea:**

- **Línea 9**: `class User(Base)` → hereda de `Base` (la que creamos en `database.py`). Esto le dice a SQLAlchemy: "esta clase es una tabla".

- **Línea 10**: `__tablename__ = "users"` → el nombre de la tabla en MySQL será `users`.

- **Línea 12**: `id: Mapped[int]` → clave primaria, se autoincrementa. Cada usuario tendrá un ID único (1, 2, 3...).

- **Línea 13**: `email: Mapped[str]` → el email del usuario.
  - `unique=True` → no pueden haber dos usuarios con el mismo email.
  - `nullable=False` → el campo es obligatorio.
  - `index=True` → crea un índice en MySQL para que buscar por email sea rápido. ¿Por qué? Porque vamos a buscar por email en cada login.

- **Línea 15**: `hashed_password` → fíjense que se llama `hashed_password`, NO `password`. **Nunca almacenamos contraseñas en texto plano.** Lo que guardamos es un hash (una versión cifrada irreversible).

- **Línea 16**: `is_active` → para poder "desactivar" usuarios sin borrarlos. `default=True` significa que al crear un usuario, por defecto está activo.

- **Línea 17**: `role` → `"user"` o `"admin"`. Por defecto todos son `"user"`.

- **Línea 18**: `created_at` → la fecha de creación. `server_default=func.now()` significa que MySQL pone la fecha automáticamente (no Python). ¿Por qué en el servidor? Porque así todos los registros usan la misma zona horaria del servidor.

**¿Qué es `Mapped[str]`?**

Es la forma moderna de SQLAlchemy (2.0+) para definir columnas con type hints. Antes se hacía `Column(String(255))`, ahora se hace `Mapped[str] = mapped_column(String(255))`. La ventaja: tu IDE sabe que `user.email` es un string y te da autocompletado.

---

### 2. `schemas/user_schema.py` — Los schemas (Validación)

```python
from datetime import datetime                                    # Línea 1

from pydantic import BaseModel, EmailStr                         # Línea 3


class UserCreate(BaseModel):                                     # Línea 6
    email: str                                                   # Línea 7
    full_name: str                                               # Línea 8
    password: str                                                # Línea 9


class UserResponse(BaseModel):                                   # Línea 12
    id: int                                                      # Línea 13
    email: str                                                   # Línea 14
    full_name: str                                               # Línea 15
    is_active: bool                                              # Línea 16
    role: str                                                    # Línea 17
    created_at: datetime                                         # Línea 18

    model_config = {"from_attributes": True}                     # Línea 20
```

**¿Qué es un schema y por qué lo necesitamos?**

Los schemas son **contratos**: definen qué datos acepta y qué datos devuelve nuestra API.

- `UserCreate` → lo que el usuario **envía** para registrarse. Fíjense que tiene `password` (texto plano que el usuario escribe).
- `UserResponse` → lo que la API **devuelve**. Fíjense que **NO tiene** `password` ni `hashed_password`. Nunca devolvemos la contraseña al usuario.

**¿Por qué no usar el modelo directamente?**

Porque el modelo tiene `hashed_password` y no queremos devolverlo. Además, el modelo recibe `hashed_password` pero el usuario envía `password` (texto plano). El schema nos permite tener **formas distintas** para la entrada y la salida.

**Línea 20**: `model_config = {"from_attributes": True}` → le dice a Pydantic: "puedes crear un `UserResponse` a partir de un objeto `User` de SQLAlchemy". Sin esto, Pydantic no sabría cómo leer los atributos del modelo.

---

### 3. `utils/security.py` — Seguridad de contraseñas (Transversal)

```python
from passlib.context import CryptContext                         # Línea 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Línea 3


def hash_password(password: str) -> str:                         # Línea 6
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:  # Línea 10
    return pwd_context.verify(plain_password, hashed_password)
```

**¿Qué es bcrypt?**

bcrypt es un **algoritmo de hashing** diseñado específicamente para contraseñas. Cuando hacemos:

```python
hash_password("MiContraseña123")
# Resultado: "$2b$12$LJ3m4ys5NzT1w3v5X7K5qeN..."
```

El resultado es un string irreversible. **No se puede "deshashear"**. Entonces, ¿cómo verificamos la contraseña en el login? Hasheamos la contraseña que el usuario escribe y comparamos los hashes:

```python
verify_password("MiContraseña123", "$2b$12$LJ3m4ys5NzT1w3v5X7K5qeN...")
# Resultado: True
```

**Línea 3**: `CryptContext(schemes=["bcrypt"], deprecated="auto")` → configuramos passlib para usar bcrypt. El `deprecated="auto"` maneja automáticamente la migración si en el futuro cambiamos de algoritmo.

**¿Por qué está en `utils/` y no en `services/`?**

Porque hashear contraseñas es una **utilidad transversal**. Podría usarse en el registro, en el cambio de contraseña, en un reset de contraseña, etc. No pertenece a una sola capa.

---

### 4. `repositories/user_repository.py` — Acceso a datos

```python
from sqlalchemy.orm import Session                               # Línea 1

from models.user_model import User                               # Línea 3


class UserRepository:                                            # Línea 6
    def __init__(self, db: Session):                             # Línea 7
        self.db = db                                             # Línea 8

    def get_by_email(self, email: str) -> User | None:           # Línea 10
        return self.db.query(User).filter(User.email == email).first()  # Línea 11

    def create(self, user: User) -> User:                        # Línea 13
        self.db.add(user)                                        # Línea 14
        self.db.commit()                                         # Línea 15
        self.db.refresh(user)                                    # Línea 16
        return user                                              # Línea 17
```

**¿Qué es el patrón Repository?**

El Repository es una **clase que encapsula todo el acceso a datos**. Es el único lugar del código que sabe cómo hablar con la base de datos. ¿Por qué? Porque si mañana cambiamos de MySQL a PostgreSQL (o a MongoDB), solo cambiamos el repository. El service no se entera.

**Línea por línea:**

- **Líneas 7-8**: El constructor recibe una `Session` de SQLAlchemy. Esto es **inyección de dependencias**: el repository no crea su propia sesión, se la pasan.

- **Líneas 10-11**: `get_by_email()` → busca un usuario por email. `.first()` devuelve el primer resultado o `None` si no encuentra nada. Equivale al SQL:
  ```sql
  SELECT * FROM users WHERE email = 'juan@email.com' LIMIT 1;
  ```

- **Línea 14**: `db.add(user)` → marca al usuario para ser insertado.
- **Línea 15**: `db.commit()` → ejecuta el INSERT en MySQL.
- **Línea 16**: `db.refresh(user)` → recarga el usuario desde la BD para obtener el `id` y `created_at` que MySQL generó automáticamente.

**¿Por qué `User | None`?**

Es un type hint de Python 3.10+. Significa: "esta función devuelve un `User` o `None`". Esto es importante porque si buscamos un email que no existe, el resultado es `None`, no un error.

---

### 5. `services/auth_service.py` — Lógica de negocio

```python
from fastapi import HTTPException, status                        # Línea 1
from sqlalchemy.orm import Session                               # Línea 2

from models.user_model import User                               # Línea 4
from repositories.user_repository import UserRepository          # Línea 5
from schemas.user_schema import UserCreate                       # Línea 6
from utils.security import hash_password                         # Línea 7


class AuthService:                                               # Línea 10
    def __init__(self, db: Session):                             # Línea 11
        self.user_repository = UserRepository(db)                # Línea 12

    def register(self, user_data: UserCreate) -> User:           # Línea 14
        existing_user = self.user_repository.get_by_email(user_data.email)  # Línea 15
        if existing_user:                                        # Línea 16
            raise HTTPException(                                 # Línea 17
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo electrónico",
            )

        new_user = User(                                         # Línea 22
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
        )

        return self.user_repository.create(new_user)             # Línea 28
```

**El Service es donde viven las reglas de negocio.** En este caso:

1. **Línea 15**: Preguntamos al repository si ya existe un usuario con ese email.
2. **Líneas 16-20**: Si existe → lanzamos un error 409 (Conflict). Esta es una **regla de negocio**: "no se pueden registrar dos usuarios con el mismo email".
3. **Líneas 22-26**: Creamos el objeto `User`. Fíjense en la **línea 25**: aquí es donde hasheamos la contraseña. El usuario envió `"MiContraseña123"` y nosotros guardamos `"$2b$12$LJ3m4..."`.
4. **Línea 28**: Le pedimos al repository que guarde el usuario en la BD.

**¿Por qué el Service y no el Controller?**

Porque la regla "email único" es **lógica de negocio**, no lógica de HTTP. Si mañana además de la API tuviéramos un comando CLI para registrar usuarios, la regla seguiría siendo la misma. Si la pusiéramos en el controller, tendríamos que duplicarla.

**Flujo completo del registro:**
```
1. Usuario envía: {"email": "juan@email.com", "full_name": "Juan", "password": "123456"}
2. Controller recibe el request y llama al Service
3. Service pregunta al Repository: ¿existe este email?
4. Repository hace el SELECT en MySQL → no existe
5. Service hashea la contraseña
6. Service le pasa el User al Repository
7. Repository hace el INSERT en MySQL
8. MySQL devuelve el usuario con id=1 y created_at=2026-06-03
9. Controller devuelve el UserResponse (sin la contraseña)
```

---

### 6. `controllers/auth_controller.py` — El controlador

```python
from fastapi import APIRouter, Depends, status                   # Línea 1
from sqlalchemy.orm import Session                               # Línea 2

from config.database import get_db                               # Línea 4
from schemas.user_schema import UserCreate, UserResponse         # Línea 5
from services.auth_service import AuthService                    # Línea 6

router = APIRouter(prefix="/auth", tags=["Autenticación"])       # Línea 8


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)  # Línea 11
def register(user_data: UserCreate, db: Session = Depends(get_db)):  # Línea 12
    service = AuthService(db)                                    # Línea 13
    return service.register(user_data)                           # Línea 14
```

**El Controller es el más delgado de todos.** Solo hace 3 cosas:
1. Recibir el request.
2. Delegarlo al Service.
3. Devolver la respuesta.

**No tiene lógica de negocio.** No valida si el email existe, no hashea contraseñas. Solo orquesta.

**Línea por línea:**

- **Línea 8**: `APIRouter(prefix="/auth", tags=["Autenticación"])` → crea un grupo de rutas. Todas empiezan con `/auth`. El `tags` es para agruparlas en Swagger.

- **Línea 11**: Los decoradores del endpoint:
  - `@router.post("/register")` → método POST en la ruta `/auth/register`
  - `response_model=UserResponse` → FastAPI filtra la respuesta para que solo incluya los campos de `UserResponse` (así nunca se filtra el `hashed_password`)
  - `status_code=201` → el código HTTP para "recurso creado exitosamente"

- **Línea 12**: `user_data: UserCreate` → FastAPI automáticamente lee el body del request y lo convierte en un `UserCreate`. Si faltan campos o tienen formato incorrecto, FastAPI devuelve un 422 sin que nosotros hagamos nada.

- **Línea 12**: `db: Session = Depends(get_db)` → aquí está la **inyección de dependencias**. FastAPI llama a `get_db()`, obtiene una sesión de BD, y se la pasa al endpoint. Al terminar, cierra la sesión automáticamente.

---

### 7. Cambios en `main.py`

Agregamos dos líneas:

```python
from controllers.auth_controller import router as auth_router    # Nueva
# ...
app.include_router(auth_router)                                  # Nueva
```

`include_router` conecta las rutas del auth_controller con la app principal. Sin esta línea, el endpoint `/auth/register` no existiría.

---

## Diagrama del flujo completo

```
POST /auth/register
{"email": "juan@email.com", "full_name": "Juan", "password": "123456"}
          │
          ▼
┌─────────────────────┐
│    auth_controller   │  ← Recibe el request
│   (Controlador)      │     Valida formato (Pydantic)
└──────────┬──────────┘
           │ llama a
           ▼
┌─────────────────────┐
│    auth_service      │  ← ¿Email ya existe? → Error 409
│  (Lógica Negocio)    │     Hashea la contraseña
└──────────┬──────────┘
           │ llama a
           ▼
┌─────────────────────┐
│   user_repository    │  ← SELECT (buscar email)
│  (Acceso a Datos)    │     INSERT (crear usuario)
└──────────┬──────────┘
           │ query
           ▼
┌─────────────────────┐
│      MySQL           │  ← Tabla: users
│   (Persistencia)     │
└─────────────────────┘
           │
           ▼
Response: {"id": 1, "email": "juan@email.com", "full_name": "Juan", ...}
(SIN la contraseña)
```

---

## ¿Cómo lo pruebo?

### Desde Swagger (http://localhost:8000/docs)
1. Buscar el endpoint `POST /auth/register`
2. Click en "Try it out"
3. Escribir el body:
```json
{
  "email": "juan@email.com",
  "full_name": "Juan Pérez",
  "password": "miContraseñaSegura123"
}
```
4. Click en "Execute"
5. Deben ver una respuesta 201 con el usuario creado (sin la contraseña)

### Probar el error de email duplicado
Ejecutar el mismo request otra vez → deben ver un error 409: "Ya existe un usuario con ese correo electrónico"

---

## Conceptos clave de esta rama

| Concepto | ¿Qué es? | ¿Dónde lo vimos? |
|----------|-----------|-------------------|
| Modelo ORM | Clase Python = Tabla en BD | `user_model.py` |
| Schema / DTO | Contrato de entrada/salida de la API | `user_schema.py` |
| Hashing | Cifrado irreversible de contraseñas | `security.py` (bcrypt) |
| Patrón Repository | Encapsular acceso a datos | `user_repository.py` |
| Lógica de Negocio | Reglas que no dependen del HTTP | `auth_service.py` |
| Controller delgado | Solo orquesta, no tiene lógica | `auth_controller.py` |
| Dependency Injection | `Depends(get_db)` inyecta la sesión | `auth_controller.py` |

---

## ¿Qué sigue?

En la siguiente rama (`feature/login`) vamos a agregar el **inicio de sesión con JWT**. El usuario enviará su email y contraseña, y si son correctos, recibirá un **token** que deberá enviar en cada request posterior para identificarse.
