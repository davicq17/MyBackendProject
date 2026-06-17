from contextlib import asynccontextmanager, contextmanager
from fastapi import FastAPI
from config.database import Base, engine
from controller.auth_controller import router as auth_router
from controller.task_controller import router as task_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

# Creamos una instancia de la aplicación FastAPI
app = FastAPI(
    title= "my Task Project",
    version="0.1",
    lifespan=lifespan
)
app.include_router(auth_router)
app.include_router(task_router)
# Definimos una ruta para la raíz de nuestra API
@app.get("/")
async def bienvenida():
    # Con FastAPI, las funciones de ruta pueden ser asíncronas (async def)
    # aunque para este ejemplo simple no es estrictamente necesario.
    return {"mensaje": "¡welcome a my API"}



