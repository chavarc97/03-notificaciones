import fastapi
from app.routes import notificaciones

app = fastapi.FastAPI(title="Microservicio - Notificaciones")

app.include_router(notificaciones.router)

@app.get("/")
def root():
    return {
        "message": "API Notificaciones Funcional. Visita /docs para ver los endpoints interactivos."
    }
