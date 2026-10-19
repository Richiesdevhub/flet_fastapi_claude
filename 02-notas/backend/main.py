from itertools import count

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Notas API")


class NotaNueva(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    titulo: str = Field(min_length=1, max_length=80)
    contenido: str = Field(default="", max_length=2000)


class Nota(NotaNueva):
    id: int


notas: dict[int, Nota] = {}
nuevo_id = count(1)


@app.get("/notas", response_model=list[Nota])
def listar_notas(q: str = Query(default="", max_length=80)):
    """Sin `q` devuelve todo; con `q` filtra por título o contenido."""
    q = q.strip().lower()
    resultado = [
        n for n in notas.values()
        if not q or q in n.titulo.lower() or q in n.contenido.lower()
    ]
    return list(reversed(resultado))  # las más recientes primero


@app.post("/notas", response_model=Nota, status_code=status.HTTP_201_CREATED)
def crear_nota(datos: NotaNueva):
    nota = Nota(id=next(nuevo_id), **datos.model_dump())
    notas[nota.id] = nota
    return nota


@app.delete("/notas/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_nota(nota_id: int):
    if notas.pop(nota_id, None) is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
