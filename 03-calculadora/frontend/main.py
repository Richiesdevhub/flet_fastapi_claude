import os

import flet as ft
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

TECLAS = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "(", ")"],
    ["C", "⌫", "^", "+"],
]


def formatear(numero: float) -> str:
    """14.0 -> '14'; 0.5 -> '0.5'."""
    if numero.is_integer() and abs(numero) < 1e15:
        return str(int(numero))
    return str(numero)


async def main(page: ft.Page):
    page.title = "Calculadora"
    page.padding = 20

    pantalla = ft.TextField(read_only=True, text_align=ft.TextAlign.RIGHT, text_size=28, value="")

    def error(texto: str):
        page.show_dialog(ft.SnackBar(ft.Text(texto)))

    async def igual(e):
        if not pantalla.value:
            return
        try:
            async with httpx.AsyncClient(base_url=API_URL, timeout=5) as cliente:
                r = await cliente.post("/calcular", json={"expresion": pantalla.value})
        except httpx.HTTPError:
            error("No se pudo conectar con el backend")
            return
        if r.status_code == 200:
            pantalla.value = formatear(r.json()["resultado"])
        else:
            error(r.json().get("detail", "Error"))
        page.update()

    async def presionar(e):
        tecla = e.control.data  # cada botón guarda su tecla en `data`
        if tecla == "C":
            pantalla.value = ""
        elif tecla == "⌫":
            pantalla.value = pantalla.value[:-1]
        else:
            pantalla.value += "**" if tecla == "^" else tecla
        page.update()

    def boton(tecla: str) -> ft.Button:
        return ft.Button(tecla, data=tecla, on_click=presionar, expand=True, height=50)

    filas = [ft.Row([boton(t) for t in fila]) for fila in TECLAS]
    filas.append(ft.Row([ft.FilledButton("=", on_click=igual, expand=True, height=50)]))
    page.add(ft.Container(ft.Column([pantalla, *filas]), width=320))


if __name__ == "__main__":
    ft.run(main)
