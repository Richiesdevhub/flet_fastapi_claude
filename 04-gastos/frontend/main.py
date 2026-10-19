import os

import flet as ft
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
CATEGORIAS = ["Comida", "Transporte", "Ocio", "Otros"]


async def api(metodo: str, ruta: str, **kwargs):
    async with httpx.AsyncClient(base_url=API_URL, timeout=5) as cliente:
        r = await cliente.request(metodo, ruta, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}


async def main(page: ft.Page):
    page.title = "Gastos"
    page.padding = 20

    descripcion = ft.TextField(label="Descripción", expand=True)
    monto = ft.TextField(label="Monto", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    categoria = ft.Dropdown(
        value=CATEGORIAS[0],
        options=[ft.DropdownOption(key=c, text=c) for c in CATEGORIAS],
        width=150,
    )
    resumen = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    lista = ft.ListView(expand=True, spacing=4)

    def aviso(texto: str):
        page.show_dialog(ft.SnackBar(ft.Text(texto)))

    async def llamar(metodo: str, ruta: str, **kwargs):
        try:
            return await api(metodo, ruta, **kwargs)
        except httpx.HTTPError:
            aviso("No se pudo completar la petición al backend")
            return None

    def fila(g: dict) -> ft.ListTile:
        async def borrar(e):
            await llamar("DELETE", f"/gastos/{g['id']}")
            await cargar()

        return ft.ListTile(
            title=ft.Text(g["descripcion"]),
            subtitle=ft.Text(g["categoria"]),
            trailing=ft.Row(
                [ft.Text(f"${g['monto']:.2f}"), ft.IconButton(ft.Icons.DELETE_OUTLINE, on_click=borrar)],
                tight=True,
            ),
        )

    async def cargar():
        gastos = await llamar("GET", "/gastos")
        datos = await llamar("GET", "/gastos/resumen")
        if gastos is None or datos is None:
            return
        lista.controls = [fila(g) for g in gastos]
        detalle = " · ".join(f"{k}: ${v:.2f}" for k, v in datos["por_categoria"].items() if v > 0)
        resumen.value = f"Total: ${datos['total']:.2f}" + (f"   ({detalle})" if detalle else "")
        page.update()

    async def agregar(e):
        try:
            valor = float((monto.value or "").replace(",", "."))
        except ValueError:
            aviso("El monto debe ser un número")
            return
        datos = {"descripcion": descripcion.value or "", "monto": valor, "categoria": categoria.value}
        if await llamar("POST", "/gastos", json=datos) is not None:
            descripcion.value = monto.value = ""
            await cargar()

    page.add(
        ft.Row([descripcion, monto, categoria]),
        ft.Button("Añadir gasto", on_click=agregar),
        resumen,
        ft.Divider(),
        lista,
    )
    await cargar()


if __name__ == "__main__":
    ft.run(main)
