import flet as ft

def main(page: ft.Page):
    page.title = "Mi Bolsillo Pro"
    page.theme_mode = "dark"
    page.bgcolor = "#0f172a"
    page.add(ft.Text("¡FUNCIONA!", size=40, color="white"))

app = ft.app(target=main)
