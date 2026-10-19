import os

import flet as ft
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


async def api(metodo: str, ruta: str, **kwargs):
    async with httpx.AsyncClient(base_url=API_URL, timeout=5) as cliente:
        r = await cliente.request(metodo, ruta, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}


async def main(page: ft.Page):
    page.title = "Notas"
    page.padding = 20

    busqueda = ft.TextField(label="Buscar", prefix=ft.Icon(ft.Icons.SEARCH))
    titulo = ft.TextField(label="Título")
    contenido = ft.TextField(label="Contenido", multiline=True, min_lines=2, max_lines=4)
    lista = ft.ListView(expand=True, spacing=8)

    def aviso(texto: str):
        page.show_dialog(ft.SnackBar(ft.Text(texto)))

    async def llamar(metodo: str, ruta: str, **kwargs):
        try:
            return await api(metodo, ruta, **kwargs)
        except httpx.HTTPError:
            aviso("No se pudo completar la petición al backend")
            return None

    def tarjeta(n: dict) -> ft.Card:
        async def borrar(e):
            await llamar("DELETE", f"/notas/{n['id']}")
            await cargar()

        return ft.Card(
            content=ft.ListTile(
                title=ft.Text(n["titulo"], weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(n["contenido"] or "(sin contenido)"),
                trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, on_click=borrar),
            )
        )

    async def cargar(e=None):
        notas = await llamar("GET", "/notas", params={"q": busqueda.value or ""})
        if notas is not None:
            lista.controls = [tarjeta(n) for n in notas]
            page.update()

    async def guardar(e):
        if not (titulo.value or "").strip():
            aviso("El título es obligatorio")
            return
        datos = {"titulo": titulo.value, "contenido": contenido.value or ""}
        if await llamar("POST", "/notas", json=datos) is not None:
            titulo.value = contenido.value = ""
            await cargar()

    busqueda.on_change = cargar  # filtra mientras se escribe
    page.add(titulo, contenido, ft.Button("Guardar nota", on_click=guardar), ft.Divider(), busqueda, lista)
    await cargar()


if __name__ == "__main__":
    ft.run(main)
