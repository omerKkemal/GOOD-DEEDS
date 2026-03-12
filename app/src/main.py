import flet as ft
import os
import json
from datetime import datetime

def main(page: ft.Page):
    # Page configuration
    page.title = "📿 متتبع قضاء الصلاة - منارتك الروحية"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#1A1A2E"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Colors
    primary_color = "#4CAF50"   # Soft green
    secondary_color = "#FFD700" # Gold
    accent_color = "#FF6B6B"    # Coral red
    surface_color = "#16213E"
    card_color = "#0F3460"

    # --------------------------
    # Set up JSON file path
    try:
        if hasattr(page, 'storage_paths') and page.storage_paths:
            app_storage = page.storage_paths.get_application_support_directory()
            if app_storage:
                os.makedirs(app_storage, exist_ok=True)
                json_path = os.path.join(app_storage, "prayer_tracker.json")
            else:
                json_path = "prayer_tracker.json"
        else:
            json_path = "prayer_tracker.json"
    except Exception as e:
        json_path = "prayer_tracker.json"
        print(f"Error setting up path: {e}, using fallback: {json_path}")

    print(f"JSON file path: {json_path}")

    # Initialize data structure
    def load_data():
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"sessions": [], "last_session_id": None}
        return {"sessions": [], "last_session_id": None}

    def save_data(data):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --------------------------
    prayers = ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"]
    prayer_icons = ["🌅", "☀️", "🌤️", "🌇", "🌙"]

    total_days = 0
    current_day = 0
    current_session_id = None
    current_session = None

    # --------------------------
    # Functions
    def calculate_days():
        if not amount.value:
            return 0
        try:
            n = int(amount.value)
        except ValueError:
            return 0
        if unit.value == "يوم":
            return n
        if unit.value == "أسبوع":
            return n * 7
        if unit.value == "شهر":
            return n * 30
        if unit.value == "سنة":
            return n * 365
        return 0

    def show_notification(message, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING if is_error else ft.Icons.CHECK_CIRCLE,
                        color=ft.Colors.ORANGE if is_error else ft.Colors.GREEN),
                ft.Text(message, color=ft.Colors.WHITE),
            ]),
            bgcolor=accent_color if is_error else card_color,
            duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    def update_stats():
        if current_session:
            completed_days = len([d for d in current_session.get("daily_tasks", []) if d.get("completed")])
            total_tasks = 0
            for day in current_session.get("daily_tasks", []):
                if day.get("completed"):
                    total_tasks += len(day.get("tasks_completed", []))
            
            stats_container.content.controls[0].content.controls[1].value = str(completed_days)
            stats_container.content.controls[1].content.controls[1].value = str(total_tasks)
            stats_container.content.controls[2].content.controls[1].value = str(total_days - current_day - 1 if current_day < total_days else 0)
            page.update()

    def save_progress():
        if current_session_id and task_column.controls:
            completed_tasks = []
            for container in task_column.controls:
                if container.content.value:
                    completed_tasks.append(container.content.label)
            
            print(f"Auto-saving: Day {current_day+1}, Tasks: {completed_tasks}")
            
            data = load_data()
            
            # Find current session
            for session in data["sessions"]:
                if session["id"] == current_session_id:
                    # Find or create daily task
                    daily_task = None
                    for task in session.get("daily_tasks", []):
                        if task["day_number"] == current_day:
                            daily_task = task
                            break
                    
                    if daily_task:
                        daily_task["tasks_completed"] = completed_tasks
                        daily_task["completed"] = len(completed_tasks) == len(task_column.controls)
                        daily_task["date"] = datetime.now().isoformat()
                    else:
                        if "daily_tasks" not in session:
                            session["daily_tasks"] = []
                        session["daily_tasks"].append({
                            "day_number": current_day,
                            "tasks_completed": completed_tasks,
                            "completed": len(completed_tasks) == len(task_column.controls),
                            "date": datetime.now().isoformat()
                        })
                    
                    # Update current_day in session
                    session["current_day"] = current_day
                    
                    # Save last session ID
                    data["last_session_id"] = current_session_id
                    break
            
            save_data(data)
            update_stats()

    def show_history(e):
        data = load_data()
        sessions = data.get("sessions", [])
        
        history_content = ft.Column([
            ft.Text("📜 سجل التقدم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
            ft.Divider(color=primary_color),
        ], scroll=ft.ScrollMode.AUTO)

        if not sessions:
            history_content.controls.append(
                ft.Container(
                    content=ft.Text("لا توجد جلسات سابقة", color=ft.Colors.GREY_400, size=16),
                    padding=20,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for session in reversed(sessions[-10:]):  # Last 10 sessions, newest first
                completed_days = len([d for d in session.get("daily_tasks", []) if d.get("completed")])
                status = "✅ مكتمل" if session.get("completed") else "⏳ قيد التقدم"
                status_color = primary_color if session.get("completed") else secondary_color
                
                def create_load_handler(sid):
                    return lambda e: load_session(sid)
                
                history_content.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"🕌 {session['qada_type']}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"📅 {session['created_at'][:10]}", size=12, color=ft.Colors.GREY_400),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.Text(f"✅ {completed_days}/{session['total_days']} أيام", color=primary_color),
                                ft.Text(status, color=status_color, size=12),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.PLAY_ARROW,
                                    icon_color=secondary_color,
                                    tooltip="استئناف",
                                    on_click=create_load_handler(session["id"]),
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ]),
                        padding=10,
                        bgcolor=card_color,
                        border_radius=10,
                        margin=ft.margin.only(bottom=5),
                    )
                )

        history_content.controls.append(ft.Container(height=10))
        history_content.controls.append(ft.ElevatedButton(
            "إغلاق",
            on_click=lambda _: close_dialog(dialog),
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=accent_color),
        ))

        dialog = ft.AlertDialog(
            title=ft.Text("السجل"),
            content=ft.Container(
                content=history_content,
                width=400,
                height=500,
                padding=10,
            ),
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def load_session(session_id):
        nonlocal current_session_id, total_days, current_day, current_session
        
        data = load_data()
        for session in data["sessions"]:
            if session["id"] == session_id:
                current_session = session
                qada_type.value = session["qada_type"]
                unit.value = session["unit"]
                amount.value = str(session["amount"])
                total_days = session["total_days"]
                current_day = session.get("current_day", 0)
                current_session_id = session_id
                
                load_day()
                next_btn.visible = True
                update_stats()
                
                if hasattr(page, 'dialog') and page.dialog:
                    page.dialog.open = False
                
                show_notification("تم تحميل الجلسة بنجاح")
                break

    def load_last_session():
        """Load the last active session on startup"""
        data = load_data()
        last_id = data.get("last_session_id")
        if last_id:
            for session in data["sessions"]:
                if session["id"] == last_id and not session.get("completed", False):
                    load_session(last_id)
                    break

    def load_day():
        task_column.controls.clear()
        next_btn.disabled = True
        next_btn.style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREY_700,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=2,
        )
        
        # Check if this day already has saved progress
        saved_completed = []
        if current_session:
            for task in current_session.get("daily_tasks", []):
                if task["day_number"] == current_day:
                    saved_completed = task.get("tasks_completed", [])
                    print(f"Found saved tasks for day {current_day+1}: {saved_completed}")
                    break
        
        # Auto-save on checkbox change
        def on_checkbox_change(e):
            check_progress(e)
            save_progress()
        
        if qada_type.value == "صلاة":
            for i, p in enumerate(prayers):
                checkbox = ft.Checkbox(
                    label=f"{prayer_icons[i]} قضاء صلاة {p}",
                    label_style=ft.TextStyle(size=16, color=ft.Colors.WHITE),
                    on_change=on_checkbox_change,
                    active_color=primary_color,
                    check_color=ft.Colors.WHITE,
                )
                if f"{prayer_icons[i]} قضاء صلاة {p}" in saved_completed:
                    checkbox.value = True
                    print(f"Restored: {prayer_icons[i]} قضاء صلاة {p}")
                
                task_column.controls.append(
                    ft.Container(
                        content=checkbox,
                        padding=5,
                        bgcolor=card_color,
                        border_radius=8,
                    )
                )
        
        if qada_type.value == "صيام":
            checkbox = ft.Checkbox(
                label="☪️ قضاء صيام يوم",
                label_style=ft.TextStyle(size=16, color=ft.Colors.WHITE),
                on_change=on_checkbox_change,
                active_color=primary_color,
                check_color=ft.Colors.WHITE,
            )
            if "☪️ قضاء صيام يوم" in saved_completed:
                checkbox.value = True
                print("Restored: ☪️ قضاء صيام يوم")
            
            task_column.controls.append(
                ft.Container(
                    content=checkbox,
                    padding=5,
                    bgcolor=card_color,
                    border_radius=8,
                )
            )
        
        remaining.value = f"📅 اليوم {current_day+1} من {total_days}"
        check_progress(None)
        update_stats()
        page.update()

    def check_progress(e):
        if task_column.controls:
            all_checked = all(container.content.value for container in task_column.controls)
            
            if all_checked:
                next_btn.disabled = False
                next_btn.style = ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=primary_color,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation=5,
                )
            else:
                next_btn.disabled = True
                next_btn.style = ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREY_700,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation=2,
                )
        
        page.update()

    def next_day(e):
        nonlocal current_day, current_session
        
        # Save before moving
        save_progress()
        
        current_day += 1
        
        # Update session in JSON
        if current_session_id:
            data = load_data()
            for session in data["sessions"]:
                if session["id"] == current_session_id:
                    session["current_day"] = current_day
                    if current_day >= total_days:
                        session["completed"] = True
                    current_session = session
                    break
            save_data(data)
        
        if current_day < total_days:
            load_day()
        else:
            task_column.controls.clear()
            task_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎉", size=60),
                        ft.Text("مبروك! تم إكمال جميع المهام", size=24, weight=ft.FontWeight.BOLD, color=secondary_color),
                        ft.Text("جزاك الله خيراً على التزامك", size=18, color=primary_color),
                        ft.ElevatedButton(
                            "بداية مهمة جديدة",
                            on_click=reset_app,
                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=accent_color, padding=15),
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                    bgcolor=card_color,
                    border_radius=15,
                )
            )
            next_btn.visible = False
            remaining.value = "🎉 تم الإكمال بنجاح"
            update_stats()
            page.update()

    def reset_app(e):
        nonlocal current_session_id, total_days, current_day, current_session
        current_session_id = None
        current_session = None
        total_days = 0
        current_day = 0
        task_column.controls.clear()
        next_btn.visible = False
        remaining.value = ""
        qada_type.value = None
        unit.value = None
        amount.value = ""
        update_stats()
        page.update()

    def generate(e):
        nonlocal total_days, current_day, current_session_id, current_session
        
        if not qada_type.value or not unit.value or not amount.value:
            show_notification("الرجاء ملء جميع الحقول", is_error=True)
            return
        
        try:
            total_days = calculate_days()
            if total_days == 0:
                show_notification("الرجاء إدخال عدد صحيح أكبر من صفر", is_error=True)
                return
            
            # Create new session
            data = load_data()
            new_id = 1
            if data["sessions"]:
                new_id = max(s["id"] for s in data["sessions"]) + 1
            
            new_session = {
                "id": new_id,
                "qada_type": qada_type.value,
                "unit": unit.value,
                "amount": int(amount.value),
                "total_days": total_days,
                "current_day": 0,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "daily_tasks": []
            }
            data["sessions"].append(new_session)
            data["last_session_id"] = new_id
            save_data(data)
            
            current_session_id = new_id
            current_session = new_session
            current_day = 0
            load_day()
            next_btn.visible = True
            update_stats()
            show_notification("تم إنشاء المهمة بنجاح")
            
        except ValueError:
            show_notification("الرجاء إدخال عدد صحيح", is_error=True)

    # --------------------------
    # UI Components
    header = ft.Container(
        content=ft.Column([
            ft.Text("📿 متتبع قضاء الصلاة", size=36, weight=ft.FontWeight.BOLD, color=secondary_color),
            ft.Text("رحلة العودة إلى الله خطوة بخطوة", size=18, color=primary_color),
            ft.Container(height=3, width=200, gradient=ft.LinearGradient(colors=[primary_color, secondary_color, accent_color]), border_radius=10),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        margin=ft.margin.only(bottom=30),
    )

    stats_container = ft.Container(
        content=ft.Row([
            ft.Container(content=ft.Column([ft.Text("📊", size=24), ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=secondary_color), ft.Text("الأيام المنجزة", size=12, color=ft.Colors.GREY_400)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), padding=10, bgcolor=card_color, border_radius=10, expand=True),
            ft.Container(content=ft.Column([ft.Text("✅", size=24), ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=primary_color), ft.Text("المهام المنجزة", size=12, color=ft.Colors.GREY_400)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), padding=10, bgcolor=card_color, border_radius=10, expand=True),
            ft.Container(content=ft.Column([ft.Text("⏳", size=24), ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=accent_color), ft.Text("المتبقي", size=12, color=ft.Colors.GREY_400)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5), padding=10, bgcolor=card_color, border_radius=10, expand=True),
        ], spacing=10),
        margin=ft.margin.only(bottom=20),
    )

    task_column = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    remaining = ft.Text("", size=18, color=secondary_color)
    next_btn = ft.ElevatedButton("➡️ التالي", disabled=True, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=primary_color, padding=20, shape=ft.RoundedRectangleBorder(radius=10), elevation=5), width=200)
    
    history_btn = ft.IconButton(icon=ft.Icons.HISTORY, icon_color=secondary_color, tooltip="السجل", on_click=show_history)

    qada_type = ft.Dropdown(label="اختر نوع العبادة", label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
                            border_color=primary_color, border_radius=10, filled=True, bgcolor=card_color, color=ft.Colors.WHITE,
                            options=[ft.dropdown.Option("صلاة", text="🕌 صلاة"), ft.dropdown.Option("صيام", text="☪️ صيام")],
                            width=300)
    unit = ft.Dropdown(label="الوحدة الزمنية", label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
                       border_color=primary_color, border_radius=10, filled=True, bgcolor=card_color, color=ft.Colors.WHITE,
                       options=[ft.dropdown.Option("يوم", text="📅 يوم"), ft.dropdown.Option("أسبوع", text="📆 أسبوع"),
                                ft.dropdown.Option("شهر", text="🌙 شهر"), ft.dropdown.Option("سنة", text="⭐ سنة")],
                       width=300)
    amount = ft.TextField(label="العدد", label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
                          border_color=primary_color, border_radius=10, filled=True, bgcolor=card_color, color=ft.Colors.WHITE,
                          keyboard_type=ft.KeyboardType.NUMBER, text_align=ft.TextAlign.RIGHT, width=300)

    next_btn.on_click = next_day

    # Main content
    main_content = ft.Column([
        header,
        stats_container,
        ft.Container(
            content=ft.Column([
                ft.Text("📝 إعداد المهمة", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
                qada_type, unit, amount,
                ft.Row([ft.ElevatedButton("✨ إنشاء القائمة", on_click=generate, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=primary_color, padding=20, shape=ft.RoundedRectangleBorder(radius=10), elevation=5), width=200), history_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=25, bgcolor=surface_color, border_radius=15, width=400, margin=ft.margin.only(bottom=20)
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("📊 التقدم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color), 
                remaining
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=20, bgcolor=surface_color, border_radius=15, width=400, margin=ft.margin.only(bottom=20)
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("✅ مهام اليوم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color), 
                ft.Divider(height=1, color=primary_color), 
                task_column
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=25, bgcolor=surface_color, border_radius=15, width=400, margin=ft.margin.only(bottom=20)
        ),
        ft.Container(content=next_btn, margin=ft.margin.only(top=10)),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

    page.add(main_content)
    
    # Load last session on startup
    load_last_session()

ft.app(target=main)
