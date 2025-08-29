from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn

from app.db import db
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
# from app import models
from app.config import settings

# Inicializar la base de datos al arrancar la app
db.init_db()

# Crear la instancia de FastAPI
app = FastAPI(
    title="API Access Control",
    description="Una API inicial limpia con FastAPI",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response
# Ruta de salud básica
@app.get("/")
async def root():
    return {"message": "¡Hola! API funcionando correctamente"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API está funcionando"}

app.include_router(users_router)
app.include_router(auth_router)

# if __name__ == "__main__":
#     uvicorn.run(app, host=settings.host, port=settings.port)
