# To-Do (lista de tareas)

**Qué aprendes:** CRUD completo: crear, leer, actualizar y borrar.

Proyecto dividido en dos partes independientes que se comunican por HTTP. **Cada parte es un proyecto `uv` con su propio entorno virtual (`.venv`)**:

```
01-todo/
├── backend/            ← FastAPI (API REST, puerto 8000)
│   ├── main.py
│   ├── pyproject.toml  ← dependencias declaradas
│   └── uv.lock         ← versiones exactas (reproducible)
└── frontend/           ← Flet (interfaz de escritorio)
    ├── main.py
    ├── pyproject.toml
    └── uv.lock
```

**Versiones probadas:** Python ≥ 3.10 · Flet 1.0.4 · FastAPI 0.146.0 · Uvicorn 0.54.0 · httpx 0.28.1 · uv 0.13.1

> ⚠️ **Mantén backend y frontend en entornos separados** (con `uv` ya lo están: cada carpeta tiene su `.venv`). Con Flet 1.0.4 el modo *web* falla si convive con FastAPI ≥ 0.145; este frontend usa el modo escritorio y no necesita FastAPI.

**Requisito previo:** tener `uv` instalado (ver el [README principal](../README.md#1-instalar-uv)). Comprueba con `uv --version`.

---

## 🔧 Backend (FastAPI)

### Ejecutar

```bash
cd backend
uv sync                              # crea .venv e instala las versiones de uv.lock
uv run uvicorn main:app --reload     # arranca el servidor
```

- API en `http://127.0.0.1:8000`
- Documentación interactiva (para probar sin frontend): `http://127.0.0.1:8000/docs`

### Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/tareas` | Lista todas las tareas |
| `POST` | `/tareas` | Crea una tarea `{"titulo": "..."}` → 201 |
| `PATCH` | `/tareas/{id}` | Cambia `titulo` y/o `completada` |
| `DELETE` | `/tareas/{id}` | Borra la tarea → 204 |

### Pasos críticos explicados

1. **Modelos Pydantic separados (`TareaNueva`, `TareaCambios`, `Tarea`)**: Lo que el cliente **envía** y lo que el servidor **devuelve** son modelos distintos. `Field(min_length=1)` + `str_strip_whitespace=True` rechazan títulos vacíos o de solo espacios con un 422 automático.
2. **`PATCH` con `exclude_unset=True`**: `cambios.model_dump(exclude_unset=True)` solo incluye los campos que el cliente realmente mandó. Así enviar `{"completada": true}` no borra el título.
3. **Códigos HTTP correctos**: `201` al crear, `204` (sin cuerpo) al borrar, `404` con `HTTPException` si el id no existe.
4. **Almacenamiento en memoria**: `tareas` es un diccionario y los ids salen de `itertools.count`. Es perfecto para aprender, pero **se pierde al reiniciar** el servidor.

---

## 🖥️ Frontend (Flet)

### Ejecutar (con el backend ya encendido, en otra terminal)

```bash
cd frontend
uv sync
uv run python main.py
```

Se abre una ventana de escritorio. Si tu backend corre en otra dirección:

```bash
API_URL=http://192.168.1.10:8000 uv run python main.py      # PowerShell: $env:API_URL="http://..."; uv run python main.py
```

Opcional: `uv run flet run main.py` recarga la ventana automáticamente al guardar cambios.

### Pasos críticos explicados

1. **Handlers `async`**: Flet 1.0 acepta funciones `async def` como `on_click`/`on_change`. Así se usa `httpx.AsyncClient` sin congelar la interfaz.
2. **Reconstruir la lista desde el servidor**: Tras cada acción se llama a `cargar()`, que pide `/tareas` y reemplaza `lista.controls`. El backend es la única fuente de verdad.
3. **`page.update()` explícito**: Cambiar propiedades (`value`, `controls`) no dibuja nada hasta llamar a `page.update()`.
4. **Errores de red sin romper la app**: `llamar()` captura `httpx.HTTPError` y muestra un aviso con `page.show_dialog(ft.SnackBar(...))`.

**Cambios de Flet 1.0 que debes conocer** (mucho código antiguo en internet ya no funciona):

- Se inicia con `ft.run(main)` (antes `ft.app(target=main)`).
- `ft.ElevatedButton` ya no existe: se usa `ft.Button` (o `ft.FilledButton`).
- Los avisos se muestran con `page.show_dialog(ft.SnackBar(...))`.
- El contenido de un botón de texto se pasa como primer argumento: `ft.Button("Texto")`.

---

## 📦 Montarlo desde cero con uv (copiar → init → add → sync)

Útil si quieres crear tu propia carpeta de trabajo en lugar de usar la incluida. Sustituye `RUTA_ZIP` por la carpeta donde descomprimiste los proyectos (la que contiene `01-todo/`).

```bash
# 0) Estructura y copia de archivos
mkdir -p mi-todo/backend mi-todo/frontend && cd mi-todo
cp RUTA_ZIP/01-todo/backend/main.py  backend/
cp RUTA_ZIP/01-todo/frontend/main.py frontend/

# 1) Backend: inicializar, añadir dependencias y sincronizar
cd backend
uv init --bare --name todo-backend
uv add "fastapi==0.146.0" "uvicorn[standard]==0.54.0"
uv sync

# 2) Frontend: lo mismo
cd ../frontend
uv init --bare --name todo-frontend
uv add "flet[cli,desktop]==1.0.4" "httpx==0.28.1"
uv sync
```

Qué hace cada comando:

- **`uv init --bare`**: crea **solo** un `pyproject.toml` y respeta tu `main.py`. Es importante usar `--bare`: el `uv init` a secas (en uv 0.13.1) genera además una carpeta `src/`, un `README.md`, un repositorio git y una configuración de paquete que aquí no se necesita.
- **`uv add`**: añade las dependencias a `pyproject.toml`, resuelve versiones, escribe `uv.lock` y las instala en `.venv`.
- **`uv sync`**: hace que `.venv` coincida exactamente con `uv.lock`. Es lo que ejecutas tras clonar o copiar un proyecto que ya trae `pyproject.toml` y `uv.lock`.
- **`uv run ...`**: ejecuta un comando dentro de ese `.venv`, sin tener que activarlo.

---

## 🩺 Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `uv: command not found` | Cierra y vuelve a abrir la terminal tras instalar uv, o revisa que su carpeta esté en el `PATH`. |
| `uv sync --locked` dice que el lock está desactualizado | Cambiaste `pyproject.toml` sin actualizar `uv.lock`: ejecuta `uv lock` (o usa `uv sync`). |
| "No se pudo conectar con el backend" | El backend no está corriendo o usa otro puerto. Revisa `API_URL`. |
| Los datos desaparecen | Es normal: el almacenamiento es en memoria. Reiniciar el backend lo vacía. |
| `Address already in use` | El puerto 8000 está ocupado: `uv run uvicorn main:app --reload --port 8001` y `API_URL=http://127.0.0.1:8001`. |
| La ventana de Flet no abre en Linux | Faltan librerías del sistema; consulta la documentación de Flet para Linux. |

## ➡️ Siguientes pasos para practicar

- Reemplaza el diccionario en memoria por SQLite (SQLModel o SQLAlchemy) con `uv add sqlmodel`.
- Añade autenticación (usuarios y tokens JWT).
- Escribe pruebas del backend: `uv add --dev pytest httpx` y usa el `TestClient` de FastAPI.
