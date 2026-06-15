# Rama 3: Login — Autenticación con JWT

## ¿Qué vamos a hacer?

Vamos a implementar el **inicio de sesión**. El usuario enviará su email y contraseña, y si son correctos, recibirá un **token JWT** que deberá enviar en cada request posterior.

Piensen en el token como una **pulsera de un festival**: en la entrada verifican tu identidad (login) y te dan una pulsera (token). Después, para entrar a cualquier escenario, solo muestras la pulsera. No tienes que volver a mostrar tu cédula cada vez.

---

## ¿Qué es JWT?

**JWT** (JSON Web Token) es un estándar para crear tokens de acceso. Un token JWT tiene 3 partes separadas por puntos:

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE3NDUwMDAwfQ.abc123firma
│                      │                                          │
│ HEADER               │ PAYLOAD                                  │ FIRMA
│ (algoritmo)          │ (datos: user_id, expiración)             │ (verificación)
```

- **Header**: dice qué algoritmo se usó para firmar (HS256).
- **Payload**: contiene los datos que nosotros metemos (el ID del usuario y cuándo expira).
- **Firma**: garantiza que nadie modificó el token. Se genera con nuestra `SECRET_KEY`.

**Importante**: el payload **NO está encriptado**, está en Base64 (cualquiera puede leerlo). Lo que SÍ está protegido es la **firma**: si alguien modifica el payload, la firma ya no coincide y el token es rechazado.

---

## ¿Qué archivos modificamos/creamos?

| Archivo | Acción | ¿Qué cambia? |
|---------|--------|---------------|
| `utils/security.py` | Modificado | Agregar `create_access_token()` y `verify_token()` |
| `schemas/user_schema.py` | Modificado | Agregar `LoginRequest` y `Token` |
| `services/auth_service.py` | Modificado | Agregar método `login()` |
| `controllers/auth_controller.py` | Modificado | Agregar endpoint `POST /auth/login` |
| `utils/dependencies.py` | **Nuevo** | `get_current_user()` — extrae el usuario del token |

---

## Archivo por archivo

### 1. `utils/security.py` — Funciones JWT (nuevas)

Se agregaron dos funciones al archivo existente:

```python
from datetime import datetime, timedelta, timezone              # Línea 1

from jose import JWTError, jwt                                   # Línea 3
from passlib.context import CryptContext                         # Línea 4

from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # Línea 6

# ... (hash_password y verify_password siguen igual) ...

def create_access_token(data: dict) -> str:                      # Línea 20
    to_encode = data.copy()                                      # Línea 21
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Línea 22
    to_encode.update({"exp": expire})                            # Línea 23
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Línea 24


def verify_token(token: str) -> dict | None:                    # Línea 27
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Línea 29
        return payload                                           # Línea 30
    except JWTError:                                             # Línea 31
        return None                                              # Línea 32
```

#### `create_access_token()` — Crear un token

- **Línea 21**: `data.copy()` → copiamos el diccionario para no modificar el original. Nosotros le pasamos `{"sub": "1"}` (el ID del usuario).
- **Línea 22**: Calculamos cuándo expira el token. `datetime.now(timezone.utc)` = ahora en UTC, `+ timedelta(minutes=30)` = dentro de 30 minutos.
- **Línea 23**: Agregamos la fecha de expiración al payload: `{"sub": "1", "exp": 2026-06-03T15:30:00}`.
- **Línea 24**: `jwt.encode()` → genera el token firmado con nuestra `SECRET_KEY`.

**¿Qué es `"sub"`?** Es una convención de JWT. `sub` = "subject" = "de quién es este token". Nosotros ponemos el ID del usuario.

#### `verify_token()` — Verificar un token

- **Línea 29**: `jwt.decode()` → decodifica el token y verifica:
  1. Que la firma sea correcta (nadie lo modificó).
  2. Que no esté expirado.
- **Línea 30**: Si todo está bien, devuelve el payload: `{"sub": "1", "exp": ...}`.
- **Líneas 31-32**: Si hay cualquier error (firma inválida, expirado, formato incorrecto), devuelve `None`.

---

### 2. `schemas/user_schema.py` — Schemas nuevos

```python
class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- `LoginRequest` → lo que el usuario envía para hacer login: email y contraseña.
- `Token` → lo que la API devuelve: el token y su tipo. El `token_type` siempre es `"bearer"` (estándar OAuth2, significa "el que tenga este token puede usarlo").

---

### 3. `services/auth_service.py` — Método `login()` (nuevo)

```python
def login(self, login_data: LoginRequest) -> Token:
    user = self.user_repository.get_by_email(login_data.email)   # Línea 1
    if not user:                                                  # Línea 2
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not verify_password(login_data.password, user.hashed_password):  # Línea 8
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not user.is_active:                                        # Línea 14
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )

    access_token = create_access_token(data={"sub": str(user.id)})  # Línea 20
    return Token(access_token=access_token)                       # Línea 21
```

**El login tiene 3 validaciones:**

1. **Líneas 1-6**: ¿Existe el usuario? Si no → 401.
2. **Líneas 8-12**: ¿La contraseña es correcta? Si no → 401.
3. **Líneas 14-18**: ¿El usuario está activo? Si no → 403.

**Detalle de seguridad importante (Líneas 2-6 y 8-12):** Fíjense que en ambos casos el mensaje es **"Credenciales inválidas"**, no "Email no encontrado" ni "Contraseña incorrecta". ¿Por qué? Porque si decimos "Email no encontrado", un atacante puede probar emails hasta encontrar uno válido. Dando el mismo mensaje genérico, no sabe si falló el email o la contraseña.

**Línea 20**: Creamos el token con el ID del usuario en el campo `"sub"`. Convertimos a string porque JWT trabaja con strings.

---

### 4. `controllers/auth_controller.py` — Endpoint de login

```python
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(login_data)
```

Igual de delgado que el register. Recibe el request, lo delega al service, devuelve la respuesta. Nada de lógica aquí.

---

### 5. `utils/dependencies.py` — La pieza clave: `get_current_user()` (NUEVO)

```python
from fastapi import Depends, HTTPException, status               # Línea 1
from fastapi.security import OAuth2PasswordBearer                # Línea 2
from sqlalchemy.orm import Session                               # Línea 3

from config.database import get_db                               # Línea 5
from models.user_model import User                               # Línea 6
from utils.security import verify_token                          # Línea 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")     # Línea 9


def get_current_user(                                            # Línea 12
    token: str = Depends(oauth2_scheme),                         # Línea 13
    db: Session = Depends(get_db),                               # Línea 14
) -> User:
    payload = verify_token(token)                                # Línea 16
    if payload is None:                                          # Línea 17
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")                            # Línea 24
    if user_id is None:                                          # Línea 25
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()  # Línea 32
    if user is None:                                             # Línea 33
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user                                                  # Línea 40
```

**Esta es la función más importante para proteger rutas.** Veamos paso a paso:

#### `OAuth2PasswordBearer` (Línea 9)
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
```
Esto le dice a FastAPI: "los tokens vienen en el header `Authorization: Bearer <token>`". El `tokenUrl` es para que Swagger sepa dónde obtener el token (el formulario de login en `/docs`).

#### La dependency (Líneas 12-40)

Esta función se va a usar como `Depends(get_current_user)` en los endpoints protegidos. Cuando un request llega a un endpoint protegido:

1. **Línea 13**: FastAPI extrae el token del header `Authorization: Bearer eyJ...`.
2. **Línea 16**: Verificamos que el token sea válido y no esté expirado.
3. **Línea 24**: Extraemos el `user_id` del payload (`"sub": "1"`).
4. **Línea 32**: Buscamos el usuario en la BD por su ID.
5. **Línea 40**: Devolvemos el objeto `User` completo.

Si cualquier paso falla → 401 Unauthorized. El endpoint nunca llega a ejecutarse.

**¿Cómo se usa en un endpoint?** (lo veremos en la siguiente rama)
```python
@router.get("/tasks")
def get_tasks(current_user: User = Depends(get_current_user)):
    # current_user ya tiene el usuario autenticado
    # Si llegó aquí, el token es válido
    pass
```

---

## Diagrama del flujo de login

```
POST /auth/login
{"email": "juan@email.com", "password": "123456"}
          │
          ▼
┌─────────────────────┐
│   auth_controller    │  ← Recibe email + password
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    auth_service      │  ← ¿Existe el usuario? ✓
│                      │     ¿Contraseña correcta? ✓
│                      │     ¿Está activo? ✓
│                      │     Genera token JWT
└─────────────────────┘
           │
           ▼
Response: {"access_token": "eyJhbGci...", "token_type": "bearer"}
```

## Diagrama del flujo de autenticación (requests protegidos)

```
GET /tasks
Header: Authorization: Bearer eyJhbGci...
          │
          ▼
┌─────────────────────┐
│  get_current_user()  │  ← Extrae token del header
│    (Dependency)      │     Verifica firma + expiración
│                      │     Busca usuario en BD
└──────────┬──────────┘
           │ ✓ Token válido
           ▼
┌─────────────────────┐
│   task_controller    │  ← Recibe el User ya autenticado
│                      │     Ejecuta la lógica del endpoint
└─────────────────────┘

           │ ✗ Token inválido
           ▼
Response: 401 {"detail": "Token inválido o expirado"}
```

---

## ¿Cómo lo pruebo?

### 1. Registrar un usuario (si no lo has hecho)
```
POST /auth/register
{
  "email": "juan@email.com",
  "full_name": "Juan Pérez",
  "password": "miContraseña123"
}
```

### 2. Hacer login
```
POST /auth/login
{
  "email": "juan@email.com",
  "password": "miContraseña123"
}
```
Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Probar errores
- Email que no existe → 401 "Credenciales inválidas"
- Contraseña incorrecta → 401 "Credenciales inválidas"
- Fíjense que el mensaje es el mismo (por seguridad)

### 4. En Swagger (/docs)
Una vez que tengan el token, en Swagger van a ver un botón **"Authorize"** (candado) arriba a la derecha. Hagan click, peguen el token, y todas las requests protegidas lo enviarán automáticamente.

---

## Conceptos clave de esta rama

| Concepto | ¿Qué es? | ¿Dónde lo vimos? |
|----------|-----------|-------------------|
| JWT | Token firmado con datos del usuario | `security.py` |
| OAuth2 Bearer | Estándar para enviar tokens en headers | `dependencies.py` |
| Dependency Injection | `Depends()` inyecta valores automáticamente | `get_current_user()` |
| Seguridad de login | Mismo mensaje para email/password incorrectos | `auth_service.py` |
| Token expiration | Tokens tienen tiempo de vida limitado | `create_access_token()` |

---

## ¿Qué sigue?

En la siguiente rama (`feature/todos`) vamos a crear el **CRUD completo de tareas** con rutas protegidas. Ahí van a usar `get_current_user()` para que cada usuario solo vea y gestione **sus propias tareas**.
