# Documento de Requerimientos del Cliente

**Cliente:** TaskFlow Solutions S.A.S  
**Contacto:** María Alejandra Gómez — Gerente de Operaciones  
**Fecha:** 3 de junio de 2026  
**Dirigido a:** Equipo de Desarrollo Backend

---

## 1. Descripción General

Somos una empresa pequeña de consultoría y necesitamos una **API para gestionar las tareas internas de nuestros empleados**. Actualmente usamos hojas de cálculo compartidas y se nos está saliendo de las manos: no sabemos quién tiene qué tarea, las prioridades se pierden, y cualquiera puede modificar las tareas de otro sin control.

Queremos un sistema donde cada empleado tenga su cuenta, gestione sus propias tareas y los administradores puedan tener visibilidad de todo.

---

## 2. Requerimientos Funcionales

### RF-01: Registro de Usuarios
- Cualquier persona debe poder registrarse proporcionando su **correo electrónico**, **nombre completo** y una **contraseña**.
- El correo electrónico debe ser único en el sistema (no se pueden registrar dos cuentas con el mismo correo).
- La contraseña debe almacenarse de forma segura (no en texto plano).
- Al registrarse, el usuario queda con rol **"user"** por defecto.

### RF-02: Inicio de Sesión
- El usuario debe poder iniciar sesión con su **correo electrónico** y **contraseña**.
- Si las credenciales son correctas, el sistema debe devolver un **token de acceso** que el usuario usará para las demás operaciones.
- El token debe tener una **duración limitada** (sugerimos 30 minutos).

### RF-03: Gestión de Tareas (CRUD)
- Un usuario autenticado debe poder:
  - **Crear** una tarea con: título, descripción (opcional), prioridad (baja, media, alta) y estado inicial "pendiente".
  - **Ver** la lista de **sus propias tareas** (no las de otros usuarios).
  - **Ver el detalle** de una tarea específica suya.
  - **Actualizar** una tarea suya: cambiar título, descripción, prioridad o estado.
  - **Eliminar** una tarea suya.
- Un usuario **no debe poder** ver, modificar ni eliminar tareas de otro usuario.

### RF-04: Estados de las Tareas
Las tareas deben tener los siguientes estados posibles:
- **Pendiente** (`pending`) — estado inicial al crear la tarea.
- **En progreso** (`in_progress`) — el empleado está trabajando en ella.
- **Completada** (`done`) — la tarea fue finalizada.

**Regla importante:** Una tarea no puede pasar directamente de "pendiente" a "completada". Debe pasar primero por "en progreso". Esto nos ayuda a tener trazabilidad del trabajo.

### RF-05: Perfil de Usuario
- El usuario autenticado debe poder **ver su perfil** (correo, nombre, fecha de registro).
- El usuario debe poder **editar su nombre** y **correo** (validando que el nuevo correo no exista).

### RF-06: Cambio de Contraseña
- El usuario autenticado debe poder **cambiar su contraseña**.
- Para hacerlo, debe proporcionar su **contraseña actual** (por seguridad) y la **nueva contraseña**.
- Si la contraseña actual no coincide, la operación debe rechazarse.

### RF-07: Roles y Permisos
Necesitamos dos roles:
- **user**: puede gestionar sus propias tareas y su perfil.
- **admin**: además de lo anterior, puede:
  - **Ver la lista de todos los usuarios** del sistema.
  - **Cambiar el rol** de un usuario (por ejemplo, promover a admin).
  - **Ver todas las tareas** de todos los usuarios (para supervisión).

Un usuario normal **no debe poder** acceder a las funcionalidades de administrador.

---

## 3. Requerimientos No Funcionales

### RNF-01: Seguridad
- Las contraseñas deben estar hasheadas (nunca en texto plano).
- Las rutas de tareas, perfil y administración deben estar protegidas (solo accesibles con token válido).
- El sistema debe validar que el token no esté expirado.

### RNF-02: Respuestas del Sistema
- Todas las respuestas deben ser en formato **JSON**.
- Los errores deben devolver mensajes claros y consistentes, no errores técnicos internos.
- Ejemplos:
  - `404` — "La tarea no fue encontrada"
  - `401` — "Credenciales inválidas"
  - `403` — "No tiene permisos para realizar esta acción"
  - `409` — "Ya existe un usuario con ese correo electrónico"

### RNF-03: Base de Datos
- Usar **MySQL** como base de datos.
- Las tareas deben estar relacionadas con el usuario que las creó.
- Registrar fecha de creación y última actualización en las tareas.

### RNF-04: Documentación
- La API debe tener **documentación automática** accesible desde el navegador (Swagger o similar).

---

## 4. Entidades Principales

### Usuario
| Campo         | Tipo     | Notas                          |
|---------------|----------|--------------------------------|
| id            | Entero   | Autogenerado                   |
| email         | Texto    | Único, obligatorio             |
| full_name     | Texto    | Obligatorio                    |
| contraseña    | Texto    | Hasheada, obligatorio          |
| activo        | Booleano | Por defecto: true              |
| rol           | Texto    | "user" o "admin", default: user|
| fecha_creación| Fecha    | Automática                     |

### Tarea
| Campo           | Tipo     | Notas                                    |
|-----------------|----------|------------------------------------------|
| id              | Entero   | Autogenerado                             |
| título          | Texto    | Obligatorio                              |
| descripción     | Texto    | Opcional                                 |
| estado          | Texto    | pending / in_progress / done             |
| prioridad       | Texto    | low / medium / high                      |
| usuario_dueño   | Entero   | Relación con el usuario que la creó      |
| fecha_creación  | Fecha    | Automática                               |
| fecha_actualización | Fecha | Se actualiza en cada modificación        |

---

## 5. Endpoints Esperados (Referencia)

| Método | Ruta                      | Descripción                        | Acceso   |
|--------|---------------------------|------------------------------------|----------|
| POST   | /auth/register            | Registro de usuario                | Público  |
| POST   | /auth/login               | Inicio de sesión                   | Público  |
| GET    | /users/me                 | Ver mi perfil                      | User     |
| PUT    | /users/me                 | Editar mi perfil                   | User     |
| POST   | /users/me/change-password | Cambiar mi contraseña              | User     |
| GET    | /users                    | Listar todos los usuarios          | Admin    |
| PUT    | /users/{id}/role          | Cambiar rol de un usuario          | Admin    |
| GET    | /tasks                    | Listar mis tareas                  | User     |
| POST   | /tasks                    | Crear tarea                        | User     |
| GET    | /tasks/{id}               | Ver detalle de mi tarea            | User     |
| PUT    | /tasks/{id}               | Actualizar mi tarea                | User     |
| DELETE | /tasks/{id}               | Eliminar mi tarea                  | User     |
| GET    | /tasks/all                | Ver todas las tareas (supervisión) | Admin    |

---

## 6. Prioridad de Entrega

Entendemos que el desarrollo se hará por fases. Nuestra prioridad es:

1. **Registro y Login** — sin esto no podemos hacer nada.
2. **CRUD de Tareas** — es el core de lo que necesitamos.
3. **Perfil y Cambio de Contraseña** — importante pero no urgente.
4. **Roles y Administración** — para la segunda fase.
5. **Manejo de errores centralizado** — pulido final.

---

*Quedamos atentos a cualquier consulta técnica. Confiamos en su criterio para las decisiones de arquitectura e implementación.*

**María Alejandra Gómez**  
Gerente de Operaciones — TaskFlow Solutions S.A.S  
maria.gomez@taskflow.com
