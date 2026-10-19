import ast
import math
import operator

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Calculadora API")

# Lista blanca: solo estas operaciones están permitidas.
BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARIOS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class Peticion(BaseModel):
    expresion: str = Field(min_length=1, max_length=100)


class Respuesta(BaseModel):
    resultado: float


def evaluar(nodo: ast.AST) -> float:
    if isinstance(nodo, ast.Expression):
        return evaluar(nodo.body)
    if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
        return float(nodo.value)  # todo en float: 9**9**9 desborda en vez de colgar el servidor
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in BINARIOS:
        return BINARIOS[type(nodo.op)](evaluar(nodo.left), evaluar(nodo.right))
    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in UNARIOS:
        return UNARIOS[type(nodo.op)](evaluar(nodo.operand))
    raise ValueError("Expresión no permitida")


@app.post("/calcular", response_model=Respuesta)
def calcular(datos: Peticion):
    # NUNCA uses eval() con texto del usuario: permite ejecutar código arbitrario.
    try:
        resultado = evaluar(ast.parse(datos.expresion.strip(), mode="eval"))
        if isinstance(resultado, complex) or not math.isfinite(resultado):
            raise ValueError("Resultado no válido")
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="División entre cero")
    except (SyntaxError, ValueError, OverflowError, TypeError):
        raise HTTPException(status_code=400, detail="Expresión inválida")
    return Respuesta(resultado=resultado)
