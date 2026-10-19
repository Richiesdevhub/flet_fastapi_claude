from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Quiz API")

# Las respuestas correctas viven SOLO en el servidor.
PREGUNTAS = [
    {"id": 1, "pregunta": "¿Qué función muestra texto en consola en Python?",
     "opciones": ["echo()", "print()", "console.log()", "write()"], "correcta": 1},
    {"id": 2, "pregunta": "¿Qué método HTTP se usa normalmente para crear un recurso?",
     "opciones": ["GET", "DELETE", "POST", "HEAD"], "correcta": 2},
    {"id": 3, "pregunta": "¿Qué tipo de dato es [1, 2, 3] en Python?",
     "opciones": ["tuple", "list", "set", "dict"], "correcta": 1},
    {"id": 4, "pregunta": "¿Qué código HTTP significa 'No encontrado'?",
     "opciones": ["200", "301", "404", "500"], "correcta": 2},
    {"id": 5, "pregunta": "¿Qué comando de Git guarda cambios en el historial local?",
     "opciones": ["git push", "git commit", "git pull", "git clone"], "correcta": 1},
]
POR_ID = {p["id"]: p for p in PREGUNTAS}


class PreguntaPublica(BaseModel):
    id: int
    pregunta: str
    opciones: list[str]


class Respuesta(BaseModel):
    id: int
    opcion: int = Field(ge=0)


class Resultado(BaseModel):
    correcta: bool
    opcion_correcta: int


@app.get("/quiz", response_model=list[PreguntaPublica])
def obtener_quiz():
    # response_model descarta el campo "correcta": nunca sale del servidor.
    return PREGUNTAS


@app.post("/quiz/responder", response_model=Resultado)
def responder(datos: Respuesta):
    pregunta = POR_ID.get(datos.id)
    if pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    if datos.opcion >= len(pregunta["opciones"]):
        raise HTTPException(status_code=422, detail="Opción fuera de rango")
    return Resultado(correcta=datos.opcion == pregunta["correcta"], opcion_correcta=pregunta["correcta"])
