import os

import flet as ft
import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


async def main(page: ft.Page):
    page.title = "Quiz"
    page.padding = 20

    # Estado de la partida (un diccionario simple basta para una app pequeña).
    estado = {"preguntas": [], "indice": 0, "puntaje": 0}
    contenedor = ft.Column(spacing=12)

    async def cargar_quiz(e=None):
        try:
            async with httpx.AsyncClient(base_url=API_URL, timeout=5) as c:
                r = await c.get("/quiz")
                r.raise_for_status()
                estado.update(preguntas=r.json(), indice=0, puntaje=0)
        except httpx.HTTPError:
            contenedor.controls = [
                ft.Text("No se pudo conectar con el backend."),
                ft.Button("Reintentar", on_click=cargar_quiz),
            ]
            page.update()
            return
        mostrar_pregunta()

    def mostrar_pregunta():
        p = estado["preguntas"][estado["indice"]]
        retroalimentacion = ft.Text("")
        siguiente = ft.Button("Siguiente", visible=False)
        botones: list[ft.Button] = []

        async def elegir(e):
            for b in botones:
                b.disabled = True
            try:
                async with httpx.AsyncClient(base_url=API_URL, timeout=5) as c:
                    r = await c.post("/quiz/responder", json={"id": p["id"], "opcion": e.control.data})
                    r.raise_for_status()
                    res = r.json()
            except httpx.HTTPError:
                retroalimentacion.value = "Error de conexión"
                page.update()
                return
            if res["correcta"]:
                estado["puntaje"] += 1
            retroalimentacion.value = "¡Correcto!" if res["correcta"] else "Incorrecto"
            botones[res["opcion_correcta"]].bgcolor = ft.Colors.GREEN_300
            if not res["correcta"]:
                e.control.bgcolor = ft.Colors.RED_300
            siguiente.visible = True
            page.update()

        def avanzar(e):
            estado["indice"] += 1
            if estado["indice"] < len(estado["preguntas"]):
                mostrar_pregunta()
            else:
                mostrar_final()

        siguiente.on_click = avanzar
        botones.extend(ft.Button(texto, data=i, on_click=elegir, width=320) for i, texto in enumerate(p["opciones"]))
        contenedor.controls = [
            ft.Text(f"Pregunta {estado['indice'] + 1} de {len(estado['preguntas'])}"),
            ft.Text(p["pregunta"], size=20, weight=ft.FontWeight.BOLD),
            *botones,
            retroalimentacion,
            siguiente,
        ]
        page.update()

    def mostrar_final():
        contenedor.controls = [
            ft.Text("Resultado final", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"{estado['puntaje']} de {len(estado['preguntas'])} correctas", size=20),
            ft.Button("Jugar de nuevo", on_click=cargar_quiz),
        ]
        page.update()

    page.add(contenedor)
    await cargar_quiz()


if __name__ == "__main__":
    ft.run(main)
