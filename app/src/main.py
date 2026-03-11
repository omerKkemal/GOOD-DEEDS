import flet as ft
import sqlite3
from datetime import datetime
import json

def main(page: ft.Page):
    # Page configuration
    page.title = "📿 متتبع قضاء الصلاة - منارتك الروحية"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#1A1A2E"  # Dark purple background
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Dark theme color scheme inspired by night sky
    primary_color = "#4CAF50"  # Soft green
    secondary_color = "#FFD700"  # Gold
    accent_color = "#FF6B6B"  # Coral red
    surface_color = "#16213E"  # Dark blue
    card_color = "#0F3460"  # Royal blue
    text_color = "#E94560"  # Pink accent
    bg_dark = "#1A1A2E"  # Dark background
    
    # Initialize database
    conn = sqlite3.connect('prayer_tracker.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qada_type TEXT NOT NULL,
            unit TEXT NOT NULL,
            amount INTEGER NOT NULL,
            total_days INTEGER NOT NULL,
            current_day INTEGER DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            day_number INTEGER NOT NULL,
            tasks_completed TEXT,  -- JSON array of completed tasks
            completed BOOLEAN DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    
    prayers = ["الفجر", "الظهر", "العصر", "المغرب", "العشاء"]
    prayer_icons = ["🌅", "☀️", "🌤️", "🌇", "🌙"]
    
    total_days = 0
    current_day = 0
    current_session_id = None
    
    # Define all functions first
    
    def calculate_days():
        if not amount.value:
            return 0
        n = int(amount.value)
        
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
        """Helper function to show notifications"""
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
        if current_session_id:
            conn = sqlite3.connect('prayer_tracker.db')
            c = conn.cursor()
            
            # Get completed days
            c.execute('''
                SELECT COUNT(*) FROM daily_tasks 
                WHERE session_id = ? AND completed = 1
            ''', (current_session_id,))
            completed_days = c.fetchone()[0]
            
            # Get total tasks completed
            c.execute('''
                SELECT tasks_completed FROM daily_tasks 
                WHERE session_id = ? AND completed = 1
            ''', (current_session_id,))
            tasks_data = c.fetchall()
            
            total_tasks = 0
            for task in tasks_data:
                if task[0]:
                    tasks = json.loads(task[0])
                    total_tasks += len(tasks)
            
            # Update stats display
            stats_container.content.controls[0].content.controls[1].value = str(completed_days)
            stats_container.content.controls[1].content.controls[1].value = str(total_tasks)
            stats_container.content.controls[2].content.controls[1].value = str(total_days - current_day - 1 if current_day < total_days else 0)
            
            conn.close()
            page.update()
    
    def save_progress():
        if current_session_id and task_column.controls:
            completed_tasks = []
            for container in task_column.controls:
                if container.content.value:
                    completed_tasks.append(container.content.label)
            
            conn = sqlite3.connect('prayer_tracker.db')
            c = conn.cursor()
            
            # Save daily tasks
            c.execute('''
                INSERT INTO daily_tasks (session_id, day_number, tasks_completed, completed)
                VALUES (?, ?, ?, ?)
            ''', (current_session_id, current_day, json.dumps(completed_tasks), 
                  len(completed_tasks) == len(task_column.controls)))
            
            conn.commit()
            conn.close()
            
            show_notification("تم حفظ التقدم بنجاح")
    
    def show_history(e):
        conn = sqlite3.connect('prayer_tracker.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT s.id, s.qada_type, s.total_days, 
                   COUNT(d.id) as completed_days,
                   s.created_at
            FROM sessions s
            LEFT JOIN daily_tasks d ON s.id = d.session_id AND d.completed = 1
            GROUP BY s.id
            ORDER BY s.created_at DESC
            LIMIT 10
        ''')
        
        sessions = c.fetchall()
        conn.close()
        
        history_content = ft.Column([
            ft.Text("📜 سجل التقدم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
            ft.Divider(color=primary_color),
        ], scroll=ft.ScrollMode.AUTO)
        
        for session in sessions:
            history_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"🕌 {session[1]}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"📅 {session[5][:10]}", size=12, color=ft.Colors.GREY_400),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Text(f"✅ {session[3]}/{session[2]} أيام", color=primary_color),
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW,
                                icon_color=secondary_color,
                                tooltip="استئناف",
                                on_click=lambda _, sid=session[0]: load_session(sid),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    padding=10,
                    bgcolor=card_color,
                    border_radius=10,
                    margin=ft.margin.only(bottom=5),
                )
            )
        
        history_content.controls.append(
            ft.Container(height=10)
        )
        
        history_content.controls.append(
            ft.ElevatedButton(
                "إغلاق",
                on_click=lambda _: close_dialog(dialog),
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=accent_color),
            )
        )
        
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
        nonlocal current_session_id, total_days, current_day
        
        conn = sqlite3.connect('prayer_tracker.db')
        c = conn.cursor()
        
        c.execute('SELECT qada_type, unit, amount, total_days, current_day FROM sessions WHERE id = ?', (session_id,))
        session = c.fetchone()
        
        if session:
            qada_type.value = session[0]
            unit.value = session[1]
            amount.value = str(session[2])
            total_days = session[3]
            current_day = session[4]
            current_session_id = session_id
            
            load_day()
            next_btn.visible = True
            save_btn.visible = True
            update_stats()
        
        conn.close()
    
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
        
        if qada_type.value == "صلاة":
            for i, p in enumerate(prayers):
                task_column.controls.append(
                    ft.Container(
                        content=ft.Checkbox(
                            label=f"{prayer_icons[i]} قضاء صلاة {p}",
                            label_style=ft.TextStyle(size=16, color=ft.Colors.WHITE),
                            on_change=check_progress,
                            active_color=primary_color,
                            check_color=ft.Colors.WHITE,
                        ),
                        padding=5,
                        bgcolor=card_color,
                        border_radius=8,
                    )
                )
        
        if qada_type.value == "صيام":
            task_column.controls.append(
                ft.Container(
                    content=ft.Checkbox(
                        label="☪️ قضاء صيام يوم",
                        label_style=ft.TextStyle(size=16, color=ft.Colors.WHITE),
                        on_change=check_progress,
                        active_color=primary_color,
                        check_color=ft.Colors.WHITE,
                    ),
                    padding=5,
                    bgcolor=card_color,
                    border_radius=8,
                )
            )
        
        remaining.value = f"📅 اليوم {current_day+1} من {total_days}"
        update_stats()
        page.update()
    
    def check_progress(e):
        if task_column.controls:
            all_checked = True
            for container in task_column.controls:
                if not container.content.value:
                    all_checked = False
                    break
            
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
        nonlocal current_day
        
        # Save current day's progress
        save_progress()
        
        current_day += 1
        
        # Update session current day
        if current_session_id:
            conn = sqlite3.connect('prayer_tracker.db')
            c = conn.cursor()
            c.execute('UPDATE sessions SET current_day = ? WHERE id = ?', 
                     (current_day, current_session_id))
            conn.commit()
            conn.close()
        
        if current_day < total_days:
            load_day()
        else:
            # Mark session as completed
            if current_session_id:
                conn = sqlite3.connect('prayer_tracker.db')
                c = conn.cursor()
                c.execute('UPDATE sessions SET completed = 1 WHERE id = ?', 
                         (current_session_id,))
                conn.commit()
                conn.close()
            
            task_column.controls.clear()
            task_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🎉", size=60, text_align=ft.TextAlign.CENTER),
                        ft.Text(
                            "مبروك! تم إكمال جميع المهام",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=secondary_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "جزاك الله خيراً على التزامك",
                            size=18,
                            color=primary_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "بداية مهمة جديدة",
                            on_click=reset_app,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=accent_color,
                                padding=15,
                            ),
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                    bgcolor=card_color,
                    border_radius=15,
                    margin=ft.margin.only(top=20),
                    border=ft.border.all(2, primary_color),
                )
            )
            next_btn.visible = False
            remaining.value = "🎉 تم الإكمال بنجاح"
            update_stats()
            page.update()
    
    def reset_app(e):
        nonlocal current_session_id, total_days, current_day
        current_session_id = None
        total_days = 0
        current_day = 0
        task_column.controls.clear()
        next_btn.visible = False
        save_btn.visible = False
        remaining.value = ""
        qada_type.value = None
        unit.value = None
        amount.value = ""
        update_stats()
        page.update()
    
    def generate(e):
        nonlocal total_days, current_day, current_session_id
        
        if not qada_type.value or not unit.value or not amount.value:
            show_notification("الرجاء ملء جميع الحقول", is_error=True)
            return
        
        try:
            total_days = calculate_days()
            if total_days == 0:
                show_notification("الرجاء إدخال عدد صحيح أكبر من صفر", is_error=True)
                return
            
            # Save session to database
            conn = sqlite3.connect('prayer_tracker.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO sessions (qada_type, unit, amount, total_days, current_day)
                VALUES (?, ?, ?, ?, ?)
            ''', (qada_type.value, unit.value, int(amount.value), total_days, 0))
            
            current_session_id = c.lastrowid
            conn.commit()
            conn.close()
            
            current_day = 0
            load_day()
            next_btn.visible = True
            save_btn.visible = True
            update_stats()
            
        except ValueError:
            show_notification("الرجاء إدخال عدد صحيح", is_error=True)
    
    # Now create UI components
    
    # Header with Islamic pattern
    header = ft.Container(
        content=ft.Column([
            ft.Text(
                "📿 متتبع قضاء الصلاة",
                size=36,
                weight=ft.FontWeight.BOLD,
                color=secondary_color,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "رحلة العودة إلى الله خطوة بخطوة",
                size=18,
                color=primary_color,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(
                height=3,
                width=200,
                gradient=ft.LinearGradient(
                    colors=[primary_color, secondary_color, accent_color],
                ),
                border_radius=10,
                margin=ft.margin.only(top=10),
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        margin=ft.margin.only(bottom=30),
    )
    
    # Stats section
    stats_container = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("📊", size=24),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
                    ft.Text("الأيام المنجزة", size=12, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=10,
                bgcolor=card_color,
                border_radius=10,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("✅", size=24),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=primary_color),
                    ft.Text("المهام المنجزة", size=12, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=10,
                bgcolor=card_color,
                border_radius=10,
                expand=True,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("⏳", size=24),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=accent_color),
                    ft.Text("المتبقي", size=12, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=10,
                bgcolor=card_color,
                border_radius=10,
                expand=True,
            ),
        ], spacing=10),
        margin=ft.margin.only(bottom=20),
    )
    
    # Task column
    task_column = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    remaining = ft.Text("", size=18, color=secondary_color, text_align=ft.TextAlign.CENTER)
    
    # Next button
    next_btn = ft.ElevatedButton(
        "➡️ التالي",
        disabled=True,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=primary_color,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=5,
        ),
        width=200,
    )
    
    # Save button
    save_btn = ft.IconButton(
        icon=ft.Icons.SAVE,
        icon_color=primary_color,
        tooltip="حفظ التقدم",
        on_click=lambda _: save_progress(),
        visible=False,
    )
    
    # History button
    history_btn = ft.IconButton(
        icon=ft.Icons.HISTORY,
        icon_color=secondary_color,
        tooltip="السجل",
        on_click=show_history,
    )
    
    # Enhanced input fields with dark theme
    qada_type = ft.Dropdown(
        label="اختر نوع العبادة",
        label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
        border_color=primary_color,
        border_radius=10,
        filled=True,
        bgcolor=card_color,
        color=ft.Colors.WHITE,
        options=[
            ft.dropdown.Option("صلاة", text="🕌 صلاة"),
            ft.dropdown.Option("صيام", text="☪️ صيام"),
        ],
        width=300,
    )
    
    unit = ft.Dropdown(
        label="الوحدة الزمنية",
        label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
        border_color=primary_color,
        border_radius=10,
        filled=True,
        bgcolor=card_color,
        color=ft.Colors.WHITE,
        options=[
            ft.dropdown.Option("يوم", text="📅 يوم"),
            ft.dropdown.Option("أسبوع", text="📆 أسبوع"),
            ft.dropdown.Option("شهر", text="🌙 شهر"),
            ft.dropdown.Option("سنة", text="⭐ سنة"),
        ],
        width=300,
    )
    
    amount = ft.TextField(
        label="العدد",
        label_style=ft.TextStyle(color=secondary_color, weight=ft.FontWeight.BOLD),
        border_color=primary_color,
        border_radius=10,
        filled=True,
        bgcolor=card_color,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
        width=300,
    )
    
    # Set the onclick handler for next button
    next_btn.on_click = next_day
    
    # Create the main content
    main_content = ft.Column([
        header,
        
        # Stats section
        stats_container,
        
        # Input section
        ft.Container(
            content=ft.Column([
                ft.Text("📝 إعداد المهمة", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
                qada_type,
                unit,
                amount,
                ft.Row([
                    ft.ElevatedButton(
                        "✨ إنشاء القائمة",
                        on_click=generate,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=primary_color,
                            padding=20,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=5,
                        ),
                        width=200,
                    ),
                    history_btn,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            padding=25,
            bgcolor=surface_color,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.BLACK38,
            ),
            margin=ft.margin.only(bottom=20),
            width=400,
            border=ft.border.all(1, primary_color),
        ),
        
        # Progress section
        ft.Container(
            content=ft.Column([
                ft.Text("📊 التقدم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
                remaining,
                ft.Row([save_btn], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=20,
            bgcolor=surface_color,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.BLACK38,
            ),
            margin=ft.margin.only(bottom=20),
            width=400,
            border=ft.border.all(1, primary_color),
        ),
        
        # Tasks section
        ft.Container(
            content=ft.Column([
                ft.Text("✅ مهام اليوم", size=20, weight=ft.FontWeight.BOLD, color=secondary_color),
                ft.Divider(height=1, color=primary_color),
                task_column,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=25,
            bgcolor=surface_color,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.BLACK38,
            ),
            margin=ft.margin.only(bottom=20),
            width=400,
            border=ft.border.all(1, primary_color),
        ),
        
        # Next button
        ft.Container(
            content=next_btn,
            margin=ft.margin.only(top=10),
        ),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    
    # Add everything to the page
    page.add(main_content)

ft.app(target=main)
