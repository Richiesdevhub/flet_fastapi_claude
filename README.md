# 5 mini-apps para aprender con Flet + FastAPI (gestionadas con uv)

Cada carpeta es un proyecto completo con su propio `README.md`, un `backend/` (FastAPI) y un `frontend/` (Flet). Cada subcarpeta es un proyecto `uv` independiente (`pyproject.toml` + `uv.lock`).

| # | Proyecto | Concepto clave |
|---|---|---|
| 01 | [To-Do](01-todo/README.md) | CRUD completo (GET/POST/PATCH/DELETE) |
| 02 | [Notas](02-notas/README.md) | Búsqueda con parámetros de consulta |
| 03 | [Calculadora](03-calculadora/README.md) | Lógica y seguridad en el backend |
| 04 | [Gastos](04-gastos/README.md) | Enums, validación y resúmenes |
| 05 | [Quiz](05-quiz/README.md) | Ocultar datos al cliente y estado en la UI |

**Versiones probadas:** Python ≥ 3.10 · Flet 1.0.4 · FastAPI 0.146.0 · Uvicorn 0.54.0 · httpx 0.28.1 · uv 0.13.1

---

## 1. Instalar uv

Comandos oficiales (documentación de Astral):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternativas: pip install uv · brew install uv · winget install --id=astral-sh.uv -e
```

Cierra y abre la terminal, y comprueba con `uv --version`.

## 2. Camino rápido: usar los proyectos tal como vienen

Los `pyproject.toml` y `uv.lock` ya están incluidos, así que basta con sincronizar. Ejemplo con el proyecto 01 (dos terminales):

```bash
# Terminal 1: backend
cd 01-todo/backend
uv sync
uv run uvicorn main:app --reload

# Terminal 2: frontend
cd 01-todo/frontend
uv sync
uv run python main.py
```

Para sincronizar los 10 entornos de una vez (macOS/Linux/Git Bash):

```bash
for d in */backend */frontend; do (cd "$d" && uv sync); done
```

## 3. Camino desde cero: copiar → inicializar → añadir → sincronizar

Crea tu propia carpeta de trabajo (por ejemplo `mis-apps`) **al lado** de la carpeta donde descomprimiste el zip. Aquí se asume que quedó como `./proyectos` (si no, ajusta la ruta `ORIGEN`):

```bash
ORIGEN=../proyectos
mkdir -p mis-apps && cd mis-apps

for p in 01-todo 02-notas 03-calculadora 04-gastos 05-quiz; do
  n=${p#*-}                                   # "01-todo" -> "todo"
  mkdir -p $p/backend $p/frontend

  # 1) Copiar los archivos de código
  cp $ORIGEN/$p/backend/main.py  $p/backend/main.py
  cp $ORIGEN/$p/frontend/main.py $p/frontend/main.py

  # 2) Inicializar con uv, 3) añadir dependencias y 4) sincronizar
  (cd $p/backend  && uv init --bare --name $n-backend  && uv add "fastapi==0.146.0" "uvicorn[standard]==0.54.0" && uv sync)
  (cd $p/frontend && uv init --bare --name $n-frontend && uv add "flet[cli,desktop]==1.0.4" "httpx==0.28.1" && uv sync)
done
```

Este bloque usa sintaxis de bash (macOS, Linux, WSL o Git Bash). En PowerShell, crea las carpetas y copia los `main.py` a mano (`New-Item -ItemType Directory`, `Copy-Item`) y ejecuta dentro de cada `backend/` y `frontend/` los comandos `uv init --bare`, `uv add` y `uv sync`, que son idénticos en todos los sistemas.

Notas:

- Uso `uv init --bare` a propósito: crea solo `pyproject.toml` y respeta tu `main.py`. El `uv init` a secas (en uv 0.13.1) añade `src/`, `README.md`, un repo git y un `build-system` que no queremos.
- Las versiones van fijadas con `==` para que funcione exactamente lo probado. Para actualizar, cambia la versión en `pyproject.toml` (o repite `uv add "paquete==X.Y.Z"`) y ejecuta `uv sync`.
- El campo `requires-python` que escribe `uv init` depende de tu Python instalado. Los proyectos incluidos usan `>=3.10`.

## 4. Comandos de uv que usarás a diario

| Comando | Para qué sirve |
|---|---|
| `uv sync` | Crea/actualiza `.venv` según `uv.lock` |
| `uv run <comando>` | Ejecuta dentro del `.venv` sin activarlo |
| `uv add <paquete>` | Añade una dependencia y la instala |
| `uv remove <paquete>` | La quita |
| `uv lock` | Regenera `uv.lock` tras editar `pyproject.toml` |

Orden sugerido de estudio: 01 → 02 → 03 → 04 → 05.
