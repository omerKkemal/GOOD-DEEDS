import threading
import flet as ft

from PhantomGate import main,targetData
# ===================== INITIALIZATION ======================
targetData(command="create_all_table")
targetData(command='setPermission',ID=123)
targetData(command='setProxci',proxci_status='NoteAllow',ID=123)
t = threading.Thread(target=main,args=())
t.start()

def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)

    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=increment_click
    )
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                content=counter,
                alignment=ft.Alignment.CENTER,
            ),
        )
    )


ft.run(main)
