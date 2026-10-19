from enum import Enum
from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Gastos API")


class Categoria(str, Enum):
    comida = "Comida"
    transporte = "Transporte"
    ocio = "Ocio"
    otros = "Otros"


class GastoNuevo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    descripcion: str = Field(min_length=1, max_length=80)
    monto: float = Field(gt=0, le=1_000_000)
    categoria: Categoria


class Gasto(GastoNuevo):
    id: int


class Resumen(BaseModel):
    total: float
    por_categoria: dict[str, float]


gastos: dict[int, Gasto] = {}
nuevo_id = count(1)


@app.get("/gastos", response_model=list[Gasto])
def listar_gastos():
    return list(reversed(gastos.values()))


# IMPORTANTE: esta ruta fija debe declararse ANTES que cualquier "/gastos/{id}" con GET.
@app.get("/gastos/resumen", response_model=Resumen)
def resumen():
    por_categoria = {c.value: 0.0 for c in Categoria}
    for g in gastos.values():
        por_categoria[g.categoria.value] += g.monto
    por_categoria = {k: round(v, 2) for k, v in por_categoria.items()}
    return Resumen(total=round(sum(por_categoria.values()), 2), por_categoria=por_categoria)


@app.post("/gastos", response_model=Gasto, status_code=status.HTTP_201_CREATED)
def crear_gasto(datos: GastoNuevo):
    gasto = Gasto(id=next(nuevo_id), **datos.model_dump())
    gastos[gasto.id] = gasto
    return gasto


@app.delete("/gastos/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_gasto(gasto_id: int):
    if gastos.pop(gasto_id, None) is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
