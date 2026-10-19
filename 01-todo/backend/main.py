from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="To-Do API")


class TareaNueva(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    titulo: str = Field(min_length=1, max_length=120)


class TareaCambios(BaseModel):
    """Todos los campos son opcionales: PATCH solo cambia lo que se envía."""
    model_config = ConfigDict(str_strip_whitespace=True)
    titulo: str | None = Field(default=None, min_length=1, max_length=120)
    completada: bool | None = None


class Tarea(TareaNueva):
    id: int
    completada: bool = False


# "Base de datos" en memoria: se borra al reiniciar el servidor.
tareas: dict[int, Tarea] = {}
nuevo_id = count(1)


@app.get("/tareas", response_model=list[Tarea])
def listar_tareas():
    return list(tareas.values())


@app.post("/tareas", response_model=Tarea, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: TareaNueva):
    tarea = Tarea(id=next(nuevo_id), titulo=datos.titulo)
    tareas[tarea.id] = tarea
    return tarea


@app.patch("/tareas/{tarea_id}", response_model=Tarea)
def actualizar_tarea(tarea_id: int, cambios: TareaCambios):
    tarea = tareas.get(tarea_id)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    # exclude_unset=True ignora los campos que el cliente no envió.
    tareas[tarea_id] = tarea.model_copy(update=cambios.model_dump(exclude_unset=True))
    return tareas[tarea_id]


@app.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(tarea_id: int):
    if tareas.pop(tarea_id, None) is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
