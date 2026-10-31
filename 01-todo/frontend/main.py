import os

import flet as ft
import httpx

import uvicorn

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


async def api(metodo: str, ruta: str, **kwargs):
    """Hace una petición al backend. Lanza httpx.HTTPError si algo falla."""
    async with httpx.AsyncClient(base_url=API_URL, timeout=5) as cliente:
        r = await cliente.request(metodo, ruta, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}


async def main(page: ft.Page):
    page.title = "To-Do"
    page.padding = 20

    entrada = ft.TextField(hint_text="Nueva tarea", expand=True, autofocus=True)
    lista = ft.ListView(expand=True, spacing=4)

    def aviso(texto: str):
        page.show_dialog(ft.SnackBar(ft.Text(texto)))

    async def llamar(metodo: str, ruta: str, **kwargs):
        """Igual que api() pero muestra un aviso en vez de romper la app."""
        try:
            return await api(metodo, ruta, **kwargs)
        except httpx.HTTPError:
            aviso("No se pudo completar la petición al backend")
            return None

    def fila(t: dict) -> ft.Row:
        async def alternar(e):
            await llamar("PATCH", f"/tareas/{t['id']}", json={"completada": e.control.value})
            await cargar()

        async def borrar(e):
            await llamar("DELETE", f"/tareas/{t['id']}")
            await cargar()

        return ft.Row(
            [
                ft.Checkbox(label=t["titulo"], value=t["completada"], on_change=alternar, expand=True),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Borrar", on_click=borrar),
            ]
        )

    async def cargar():
        tareas = await llamar("GET", "/tareas")
        if tareas is not None:
            lista.controls = [fila(t) for t in tareas]
            page.update()

    async def agregar(e):
        titulo = entrada.value.strip()
        if not titulo:
            return
        if await llamar("POST", "/tareas", json={"titulo": titulo}) is not None:
            entrada.value = ""
            await cargar()

    entrada.on_submit = agregar
    page.add(ft.Row([entrada, ft.Button("Añadir", on_click=agregar)]), lista)
    await cargar()


if __name__ == "__main__":
    ft.run(main)
    # ft.run(main, view=ft.AppView.WEB_BROWSER)
