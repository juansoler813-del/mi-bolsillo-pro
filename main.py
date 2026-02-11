import flet as ft

app = ft.app(target=lambda: None)

def main(page: ft.Page):
    page.title = "Mi Bolsillo Pro"
    page.theme_mode = "dark"
    page.bgcolor = "#0f172a"
    page.add(ft.Text("SI ESTO FUNCIONA, YA CASI", size=30, color="white"))

if __name__ == "__main__":
    ft.app(target=main)
