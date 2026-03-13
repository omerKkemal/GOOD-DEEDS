import flet as ft
import os
import json

def main(page: ft.Page):
    # --- Page Configuration ---
    page.title = "📿 Prayer Qada Tracker"
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

    # --- Language Support ---
    current_lang = "am"  # default: Amharic

    translations = {
        "ar": {
            "title": "📿 متتبع قضاء الصلاة",
            "app_name": "📿 منارة القضاء",
            "stats_completed": "📊 الأيام المكتملة",
            "stats_remaining": "⏳ الأيام المتبقية",
            "section_new": "إعداد ورد جديد",
            "label_worship": "العبادة",
            "label_unit": "الوحدة",
            "label_amount": "العدد",
            "option_prayer": "صلاة",
            "option_fasting": "صيام",
            "option_day": "يوم",
            "option_week": "أسبوع",
            "option_month": "شهر",
            "option_year": "سنة",
            "button_create_update": "✨ إنشاء / تحديث الجدول",
            "button_next": "⬅️ اليوم التالي",
            "prayer_fajr": "🌅 الفجر",
            "prayer_dhuhr": "☀️ الظهر",
            "prayer_asr": "🌤️ العصر",
            "prayer_maghrib": "🌇 المغرب",
            "prayer_isha": "🌙 العشاء",
            "fasting_day": "☪️ صيام يوم",
            "remaining_text": "📅 اليوم {current} من {total}",
            "completion_message": "🎉 تم الإكمال بنجاح!",
            "menu_active_sessions": "📂 الجلسات النشطة",
            "menu_no_sessions": "لا توجد جلسات",
            "menu_active_indicator": " ✅",
            "language": "اللغة",
        },
        "am": {
            "title": "📿 የሶላት ቅዳእ መከታተያ",  # corrected from ቅጣት
            "app_name": "📿 ሚናራ ቅዳእ",          # corrected from ቅጣት
            "stats_completed": "📊 የተጠናቀቁ ቀናት",
            "stats_remaining": "⏳ የቀሩ ቀናት",
            "section_new": "አዲስ ውርድ ማዘጋጀት",
            "label_worship": "አምልኮ",
            "label_unit": "ክፍል",
            "label_amount": "ቁጥር",
            "option_prayer": "ሶላት",
            "option_fasting": "ጾም",
            "option_day": "ቀን",
            "option_week": "ሳምንት",
            "option_month": "ወር",
            "option_year": "ዓመት",
            "button_create_update": "✨ ፍጠር / አዘምን ሰንጠረዥ",
            "button_next": "⬅️ የሚቀጥለው ቀን",
            "prayer_fajr": "🌅 ፈጅር",
            "prayer_dhuhr": "☀️ ዙህር",
            "prayer_asr": "🌤️ ዓስር",
            "prayer_maghrib": "🌇 መግሪብ",
            "prayer_isha": "🌙 ዒሻ",
            "fasting_day": "☪️ የጾም ቀን",
            "remaining_text": "📅 ቀን {current} ከ {total}",
            "completion_message": "🎉 በተሳካ ሁኔታ ተጠናቋል!",
            "menu_active_sessions": "📂 ንቁ ክፍለ ጊዜዎች",
            "menu_no_sessions": "ምንም ክፍለ ጊዜ የለም",
            "menu_active_indicator": " ✅",
            "language": "ቋንቋ",
        },
        "en": {
            "title": "📿 Prayer Qada Tracker",
            "app_name": "📿 Minaret of Qada",
            "stats_completed": "📊 Completed Days",
            "stats_remaining": "⏳ Remaining Days",
            "section_new": "Setup New Session",
            "label_worship": "Worship",
            "label_unit": "Unit",
            "label_amount": "Amount",
            "option_prayer": "Prayer",
            "option_fasting": "Fasting",
            "option_day": "Day",
            "option_week": "Week",
            "option_month": "Month",
            "option_year": "Year",
            "button_create_update": "✨ Create / Update Schedule",
            "button_next": "⬅️ Next Day",
            "prayer_fajr": "🌅 Fajr",
            "prayer_dhuhr": "☀️ Dhuhr",
            "prayer_asr": "🌤️ Asr",
            "prayer_maghrib": "🌇 Maghrib",
            "prayer_isha": "🌙 Isha",
            "fasting_day": "☪️ Fasting Day",
            "remaining_text": "📅 Day {current} of {total}",
            "completion_message": "🎉 Completed successfully!",
            "menu_active_sessions": "📂 Active Sessions",
            "menu_no_sessions": "No sessions",
            "menu_active_indicator": " ✅",
            "language": "Language",
        }
    }

    def _(key, **kwargs):
        text = translations[current_lang].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_task_label(task_key):
        if task_key == "fasting":
            return _("fasting_day")
        else:
            return _(f"prayer_{task_key}")

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

    # --- UI References (globally accessible) ---
    stat_done_text = ft.Text("0", size=20, weight="bold")
    stat_rem_text = ft.Text("0", size=20, weight="bold", color=accent_color)
    
    # Create input fields (will be updated in rebuild_ui)
    qada_type = ft.Dropdown(label=_("label_worship"), width=180)
    unit = ft.Dropdown(label=_("label_unit"), width=120, value="يوم")
    amount = ft.TextField(label=_("label_amount"), width=120, keyboard_type=ft.KeyboardType.NUMBER)

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
                migrate_tasks(s)
                state["session"] = s
                state["session_id"] = session_id
                state["total_days"] = s["total_days"]
                state["current_day"] = s.get("current_day", 0)
                rebuild_ui()
                break

    def migrate_tasks(session):
        for day in session.get("daily_tasks", []):
            tasks = day.get("tasks_completed", [])
            if tasks and all(isinstance(t, str) and (t.startswith("🌅") or t.startswith("☪️") or "الفجر" in t or "Fajr" in t or "ፈጅር" in t) for t in tasks):
                new_tasks = []
                for label in tasks:
                    if "الفجر" in label or "Fajr" in label or "ፈጅር" in label:
                        new_tasks.append("fajr")
                    elif "الظهر" in label or "Dhuhr" in label or "ዙህር" in label:
                        new_tasks.append("dhuhr")
                    elif "العصر" in label or "Asr" in label or "ዓስር" in label:
                        new_tasks.append("asr")
                    elif "المغرب" in label or "Maghrib" in label or "መግሪብ" in label:
                        new_tasks.append("maghrib")
                    elif "العشاء" in label or "Isha" in label or "ዒሻ" in label:
                        new_tasks.append("isha")
                    elif "صيام" in label or "Fasting" in label or "ጾም" in label:
                        new_tasks.append("fasting")
                    else:
                        new_tasks.append(label)
                day["tasks_completed"] = new_tasks

    def render_tasks():
        # Create a column specifically for checkboxes with identifiable data
        task_column = ft.Column(spacing=10, data="tasks_checkboxes")
        saved_tasks = []
        if state["session"]:
            for d in state["session"].get("daily_tasks", []):
                if d["day_number"] == state["current_day"]:
                    saved_tasks = d.get("tasks_completed", [])
                    break

        if state["session"] and state["session"]["qada_type"] == "صلاة":
            task_keys = ["fajr", "dhuhr", "asr", "maghrib", "isha"]
        else:
            task_keys = ["fasting"]

        for key in task_keys:
            label = get_task_label(key)
            cb = ft.Checkbox(
                label=label,
                value=(key in saved_tasks),
                data=key,
                on_change=lambda e: sync_progress()
            )
            task_column.controls.append(ft.Container(content=cb, padding=10, bgcolor=card_color, border_radius=8))
        return task_column

    def sync_progress():
        if not state["session_id"]:
            return

        # Find the outer container (tasks_section) which has data="task_column_container"
        outer_container = None
        for control in page.controls[0].controls:
            if isinstance(control, ft.Container) and control.data == "task_column_container":
                outer_container = control
                break
        if not outer_container:
            return

        # The outer_container.content is the Column containing [remaining_text, task_column, Divider, next_btn_container]
        outer_column = outer_container.content
        # Find the inner column with data="tasks_checkboxes"
        task_column = None
        for control in outer_column.controls:
            if isinstance(control, ft.Column) and control.data == "tasks_checkboxes":
                task_column = control
                break
        if not task_column:
            return

        done_keys = []
        for container in task_column.controls:
            cb = container.content
            if cb.value:
                done_keys.append(cb.data)

        data = load_data()
        for s in data["sessions"]:
            if s["id"] == state["session_id"]:
                tasks = s.setdefault("daily_tasks", [])
                found = False
                for t in tasks:
                    if t["day_number"] == state["current_day"]:
                        t["tasks_completed"] = done_keys
                        t["completed"] = (len(done_keys) == len(task_column.controls))
                        found = True
                        break
                if not found:
                    tasks.append({
                        "day_number": state["current_day"],
                        "tasks_completed": done_keys,
                        "completed": (len(done_keys) == len(task_column.controls))
                    })
                s["current_day"] = state["current_day"]
                state["session"] = s
        save_data(data)
        update_stats()

        # Update next button
        all_done = len(done_keys) == len(task_column.controls)
        next_btn_container = None
        for control in page.controls[0].controls:
            if isinstance(control, ft.Container) and control.data == "next_btn_container":
                next_btn_container = control
                break
        if next_btn_container:
            btn = next_btn_container.content
            btn.disabled = not all_done
            btn.bgcolor = primary_color if all_done else ft.Colors.GREY_700
            page.update()

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
        rebuild_ui()

    def create_or_update_session(e):
        if not qada_type.value or not amount.value:
            return
        try:
            n = int(amount.value)
        except ValueError:
            return

        mult = {"يوم": 1, "أسبوع": 7, "شهر": 30, "سنة": 365}
        total = n * mult.get(unit.value, 1)

        data = load_data()
        existing_session = None
        for s in data["sessions"]:
            if s["qada_type"] == qada_type.value and not s.get("completed", False):
                existing_session = s
                break

        if existing_session:
            old_total = existing_session["total_days"]
            existing_session["amount"] = n
            existing_session["unit"] = unit.value
            existing_session["total_days"] = total

            if total < old_total:
                if existing_session["current_day"] >= total:
                    existing_session["current_day"] = max(0, total - 1)
                existing_session["daily_tasks"] = [
                    d for d in existing_session["daily_tasks"]
                    if d["day_number"] < total
                ]

            save_data(data)
            if state["session_id"] == existing_session["id"]:
                state["session"] = existing_session
                state["total_days"] = total
                state["current_day"] = existing_session["current_day"]
            rebuild_ui()
        else:
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

    def change_language(new_lang):
        nonlocal current_lang
        if new_lang != current_lang:
            current_lang = new_lang
            page.rtl = (current_lang == "ar")
            rebuild_ui()

    # --- UI Rebuild Function ---
    def rebuild_ui():
        data = load_data()
        active_sessions = [s for s in data["sessions"] if not s.get("completed")]

        # Update input fields options and values
        qada_type.label = _("label_worship")
        qada_type.options = [
            ft.dropdown.Option(key="صلاة", text=_("option_prayer")),
            ft.dropdown.Option(key="صيام", text=_("option_fasting")),
        ]
        if state["session"]:
            qada_type.value = state["session"]["qada_type"]
        else:
            qada_type.value = None

        unit.label = _("label_unit")
        unit.options = [
            ft.dropdown.Option(key="يوم", text=_("option_day")),
            ft.dropdown.Option(key="أسبوع", text=_("option_week")),
            ft.dropdown.Option(key="شهر", text=_("option_month")),
            ft.dropdown.Option(key="سنة", text=_("option_year")),
        ]
        if state["session"]:
            unit.value = state["session"].get("unit", "يوم")
        else:
            unit.value = "يوم"

        amount.label = _("label_amount")
        if state["session"]:
            amount.value = str(state["session"]["amount"])
        else:
            amount.value = ""

        # Language dropdown - updated to use on_select (Flet v0.27.0+)
        lang_options = [
            ft.dropdown.Option(key="ar", text="العربية"),
            ft.dropdown.Option(key="am", text="አማርኛ"),
            ft.dropdown.Option(key="en", text="English"),
        ]
        lang_dropdown = ft.Dropdown(
            label=_("language"),
            value=current_lang,
            options=lang_options,
            width=150,
            on_select=lambda e: change_language(e.control.value)
        )

        # Menu items for active sessions
        session_items = []
        for s in active_sessions:
            migrate_tasks(s)
            type_display = _("option_prayer") if s["qada_type"] == "صلاة" else _("option_fasting")
            check = _("menu_active_indicator") if s["id"] == state["session_id"] else ""
            session_items.append(
                ft.MenuItemButton(
                    content=ft.Text(f"{type_display} ({_('option_day')} {s.get('current_day',0)+1}){check}"),
                    on_click=lambda _, sid=s["id"]: load_session(sid)
                )
            )

        menu_bar = ft.MenuBar(
            style=ft.MenuStyle(bgcolor=surface_color),
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(_("menu_active_sessions")),
                    controls=session_items if session_items else [ft.MenuItemButton(content=ft.Text(_("menu_no_sessions")))]
                ),
            ]
        )

        top_row = ft.Row([
            menu_bar,
            ft.Container(expand=True),
            lang_dropdown,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        stats_row = ft.Row([
            ft.Container(
                content=ft.Column([ft.Text(_("stats_completed"), size=12), stat_done_text], horizontal_alignment="center"),
                expand=True, bgcolor=card_color, padding=15, border_radius=10
            ),
            ft.Container(
                content=ft.Column([ft.Text(_("stats_remaining"), size=12), stat_rem_text], horizontal_alignment="center"),
                expand=True, bgcolor=card_color, padding=15, border_radius=10
            ),
        ], spacing=20)

        input_section = ft.Container(
            ft.Column([
                ft.Text(_("section_new"), size=18, weight="bold"),
                ft.Row([qada_type, unit, amount], alignment="center", wrap=True),
                ft.ElevatedButton(
                    _("button_create_update"),
                    on_click=create_or_update_session,
                    bgcolor=primary_color,
                    color="white",
                    width=200
                )
            ], horizontal_alignment="center", spacing=15),
            padding=20, bgcolor=surface_color, border_radius=15, width=500
        )

        # Tasks section
        if state["session"] and state["current_day"] < state["total_days"]:
            task_column = render_tasks()  # This column has data="tasks_checkboxes"
            remaining_text = ft.Text(
                _("remaining_text", current=state["current_day"]+1, total=state["total_days"]),
                color=secondary_color, size=18, weight="bold"
            )
            next_btn = ft.ElevatedButton(
                _("button_next"),
                on_click=next_day_trigger,
                bgcolor=primary_color,
                color="white",
                height=50,
            )
            # Determine initial all_done state
            all_done = all(cb.content.value for cb in task_column.controls)
            next_btn.disabled = not all_done
            next_btn.bgcolor = primary_color if all_done else ft.Colors.GREY_700
        else:
            task_column = ft.Column()  # empty
            if state["session"] and state["current_day"] >= state["total_days"]:
                remaining_text = ft.Text(_("completion_message"), color=secondary_color, size=18, weight="bold")
            else:
                remaining_text = ft.Text("", color=secondary_color, size=18, weight="bold")
            next_btn = ft.ElevatedButton(
                _("button_next"),
                visible=False,
                bgcolor=primary_color,
                color="white",
                height=50
            )

        tasks_section = ft.Container(
            ft.Column([
                remaining_text,
                task_column,
                ft.Divider(height=10, color="transparent"),
                next_btn
            ], horizontal_alignment="center"),
            padding=20, bgcolor=surface_color, border_radius=15, width=500,
            data="task_column_container"  # identifier for the outer container
        )
        # Wrap next_btn in a container with data for easy retrieval in sync_progress
        next_btn_container = ft.Container(content=next_btn, data="next_btn_container")
        tasks_section.content.controls[-1] = next_btn_container  # replace next_btn with container

        main_col = ft.Column([
            top_row,
            ft.Container(height=10),
            ft.Text(_("app_name"), size=32, weight="bold", color=secondary_color),
            stats_row,
            input_section,
            tasks_section
        ], horizontal_alignment="center", spacing=25)

        page.controls.clear()
        page.add(main_col)
        page.update()

    # Initial rebuild
    rebuild_ui()

ft.app(target=main)
