import flet as ft
import os
import json

def main(page: ft.Page):
    # --- Page Configuration ---
    page.title = "📿 متتبع قضاء الصلاة"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#1A1A2E"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Colors
    primary_color = "#4CAF50"
    secondary_color = "#FFD700"
    accent_color = "#FF6B6B"
    surface_color = "#16213E"
    card_color = "#0F3460"

    json_path = "prayer_tracker.json"

    # --- Data Persistence ---
    def load_data():
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if "sessions" in data else {"sessions": []}
            except:
                return {"sessions": []}
        return {"sessions": []}

    def save_data(data):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- App State ---
    state = {
        "total_days": 0,
        "current_day": 0,
        "session_id": None,
        "session": None
    }

    # --- UI References (Replacing the 'id' property) ---
    stat_done_text = ft.Text("0", size=20, weight="bold")
    stat_rem_text = ft.Text("0", size=20, weight="bold", color=accent_color)
    
    qada_type = ft.Dropdown(label="العبادة", options=[ft.dropdown.Option("صلاة"), ft.dropdown.Option("صيام")], width=180)
    unit = ft.Dropdown(label="الوحدة", value="يوم", options=[ft.dropdown.Option("يوم"), ft.dropdown.Option("أسبوع"), ft.dropdown.Option("شهر"), ft.dropdown.Option("سنة")], width=120)
    amount = ft.TextField(label="العدد", width=120, keyboard_type=ft.KeyboardType.NUMBER)
    
    task_column = ft.Column(spacing=10)
    remaining_text = ft.Text("", color=secondary_color, size=18, weight="bold")
    next_btn = ft.ElevatedButton("⬅️ اليوم التالي", visible=False, bgcolor=primary_color, color="white", height=50)

    # --- Logic Functions ---
    def update_stats():
        if state["session"]:
            done = len([d for d in state["session"].get("daily_tasks", []) if d.get("completed")])
            stat_done_text.value = str(done)
            stat_rem_text.value = str(max(0, state["total_days"] - state["current_day"]))
            page.update()

    def load_session(session_id):
        data = load_data()
        for s in data["sessions"]:
            if s["id"] == session_id:
                state["session"] = s
                state["session_id"] = session_id
                state["total_days"] = s["total_days"]
                state["current_day"] = s.get("current_day", 0)
                
                # Sync Input Fields
                qada_type.value = s["qada_type"]
                amount.value = str(s["amount"])
                
                render_tasks()
                update_stats()
                update_menu() 
                break

    def render_tasks():
        task_column.controls.clear()
        saved_tasks = []
        if state["session"]:
            for d in state["session"].get("daily_tasks", []):
                if d["day_number"] == state["current_day"]:
                    saved_tasks = d.get("tasks_completed", [])
                    break
        
        items = (["🌅 الفجر", "☀️ الظهر", "🌤️ العصر", "🌇 المغرب", "🌙 العشاء"] 
                 if qada_type.value == "صلاة" else ["☪️ صيام يوم"])
        
        for item in items:
            cb = ft.Checkbox(
                label=item, 
                value=(item in saved_tasks),
                on_change=lambda _: sync_progress()
            )
            task_column.controls.append(ft.Container(content=cb, padding=10, bgcolor=card_color, border_radius=8))
        
        remaining_text.value = f"📅 اليوم {state['current_day']+1} من {state['total_days']}"
        next_btn.visible = True
        next_btn.on_click = next_day_trigger
        update_button_state()
        page.update()

    def update_button_state():
        all_done = all(c.content.value for c in task_column.controls) if task_column.controls else False
        next_btn.disabled = not all_done
        next_btn.bgcolor = primary_color if all_done else ft.Colors.GREY_700
        page.update()

    def sync_progress():
        if not state["session_id"]: return
        done_list = [c.content.label for c in task_column.controls if c.content.value]
        data = load_data()
        for s in data["sessions"]:
            if s["id"] == state["session_id"]:
                tasks = s.setdefault("daily_tasks", [])
                found = False
                for t in tasks:
                    if t["day_number"] == state["current_day"]:
                        t["tasks_completed"] = done_list
                        t["completed"] = (len(done_list) == len(task_column.controls))
                        found = True
                        break
                if not found:
                    tasks.append({
                        "day_number": state["current_day"], 
                        "tasks_completed": done_list, 
                        "completed": (len(done_list) == len(task_column.controls))
                    })
                s["current_day"] = state["current_day"]
                state["session"] = s
        save_data(data)
        update_stats()
        update_button_state()

    def next_day_trigger(e):
        sync_progress()
        state["current_day"] += 1
        data = load_data()
        for s in data["sessions"]:
            if s["id"] == state["session_id"]:
                s["current_day"] = state["current_day"]
                if state["current_day"] >= state["total_days"]: 
                    s["completed"] = True
        save_data(data)
        
        if state["current_day"] < state["total_days"]:
            render_tasks()
        else:
            remaining_text.value = "🎉 تم الإكمال بنجاح!"
            next_btn.visible = False
            page.update()

    def create_new_session(e):
        if not qada_type.value or not amount.value: 
            return
        try:
            n = int(amount.value)
        except ValueError:
            return
            
        mult = {"يوم": 1, "أسبوع": 7, "شهر": 30, "سنة": 365}
        total = n * mult.get(unit.value, 1)
        
        data = load_data()
        new_id = max([s["id"] for s in data["sessions"]], default=0) + 1
        new_s = {
            "id": new_id, 
            "qada_type": qada_type.value, 
            "amount": n, 
            "unit": unit.value, 
            "total_days": total, 
            "current_day": 0, 
            "completed": False, 
            "daily_tasks": []
        }
        data["sessions"].append(new_s)
        save_data(data)
        
        load_session(new_id)
        update_menu()

    # --- MenuBar Logic ---
    def update_menu():
        data = load_data()
        active_sessions = [s for s in data["sessions"] if not s.get("completed")]
        
        session_items = []
        for s in active_sessions:
            # Fix: Create a closure to capture the session ID correctly
            def create_session_handler(sid):
                return lambda _: load_session(sid)
            
            check = " ✅" if s["id"] == state["session_id"] else ""
            session_items.append(
                ft.MenuItemButton(
                    content=ft.Text(f"{s['qada_type']} (يوم {s.get('current_day',0)+1}){check}"),
                    on_click=create_session_handler(s["id"])
                )
            )

        # Create the menu bar
        menu_bar = ft.MenuBar(
            style=ft.MenuStyle(bgcolor=surface_color),
            controls=[
                ft.SubmenuButton(
                    content=ft.Text("📂 الجلسات النشطة"),
                    controls=session_items if session_items else [ft.MenuItemButton(content=ft.Text("لا توجد جلسات"))]
                ),
            ]
        )
        
        # Clear and add the menu bar to the page
        page.controls.clear()
        page.add(
            ft.Column([
                menu_bar,  # Add menu bar at the top
                ft.Container(height=20),  # Add some spacing
                ft.Text("📿 منارة القضاء", size=32, weight="bold", color=secondary_color),
                stats_row,
                ft.Container(
                    ft.Column([
                        ft.Text("إعداد ورد جديد", size=18, weight="bold"),
                        ft.Row([qada_type, unit, amount], alignment="center", wrap=True),
                        ft.ElevatedButton("✨ إنشاء الجدول", on_click=create_new_session, bgcolor=primary_color, color="white", width=200)
                    ], horizontal_alignment="center", spacing=15),
                    padding=20, bgcolor=surface_color, border_radius=15, width=500
                ),
                ft.Container(
                    ft.Column([
                        remaining_text, 
                        task_column, 
                        ft.Divider(height=10, color="transparent"),
                        next_btn
                    ], horizontal_alignment="center"),
                    padding=20, bgcolor=surface_color, border_radius=15, width=500
                )
            ], horizontal_alignment="center", spacing=25)
        )
        page.update()

    # --- Layout Construction ---
    stats_row = ft.Row([
        ft.Container(
            content=ft.Column([ft.Text("📊 الأيام المكتملة", size=12), stat_done_text], horizontal_alignment="center"), 
            expand=True, bgcolor=card_color, padding=15, border_radius=10
        ),
        ft.Container(
            content=ft.Column([ft.Text("⏳ الأيام المتبقية", size=12), stat_rem_text], horizontal_alignment="center"), 
            expand=True, bgcolor=card_color, padding=15, border_radius=10
        ),
    ], spacing=20)

    # Initial layout (without menu bar - will be added by update_menu)
    page.add(
        ft.Column([
            ft.Text("📿 منارة القضاء", size=32, weight="bold", color=secondary_color),
            stats_row,
            ft.Container(
                ft.Column([
                    ft.Text("إعداد ورد جديد", size=18, weight="bold"),
                    ft.Row([qada_type, unit, amount], alignment="center", wrap=True),
                    ft.ElevatedButton("✨ إنشاء الجدول", on_click=create_new_session, bgcolor=primary_color, color="white", width=200)
                ], horizontal_alignment="center", spacing=15),
                padding=20, bgcolor=surface_color, border_radius=15, width=500
            ),
            ft.Container(
                ft.Column([
                    remaining_text, 
                    task_column, 
                    ft.Divider(height=10, color="transparent"),
                    next_btn
                ], horizontal_alignment="center"),
                padding=20, bgcolor=surface_color, border_radius=15, width=500
            )
        ], horizontal_alignment="center", spacing=25)
    )

    update_menu()

ft.app(target=main)