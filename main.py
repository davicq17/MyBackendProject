from contextlib import asynccontextmanager, contextmanager
from fastapi import FastAPI
from config.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

# Creamos una instancia de la aplicación FastAPI
app = FastAPI(
    title= "my Task Project",
    vcersion="0.1",
    lifespan=lifespan
)

# Definimos una ruta para la raíz de nuestra API
@app.get("/")
async def bienvenida():
    # Con FastAPI, las funciones de ruta pueden ser asíncronas (async def)
    # aunque para este ejemplo simple no es estrictamente necesario.
    return {"mensaje": "¡welcome a my API"}



