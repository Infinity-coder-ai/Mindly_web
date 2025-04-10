from nicegui import ui
from datetime import datetime, timedelta
from database import Database

db = Database()

def show_planner(container):
    """Display the study planner interface"""
    with container:
        ui.label('Study Planner').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            ui.label('Organize your study schedule and track your progress').classes('text-gray-600')
            
            # Calendar view toggle
            with ui.card().classes('w-full p-4'):
                ui.label('Calendar View').classes('font-bold mb-2')
                with ui.tabs().classes('w-full') as tabs:
                    ui.tab('Day View', icon='today')
                    ui.tab('Week View', icon='view_week')
                    ui.tab('Month View', icon='calendar_month')
                
                with ui.tab_panels(tabs, value='Day View').classes('w-full mt-2'):
                    with ui.tab_panel('Day View'):
                        show_day_view()
                    with ui.tab_panel('Week View'):
                        show_week_view()
                    with ui.tab_panel('Month View'):
                        show_month_view()
            
            # Upcoming assignments
            with ui.card().classes('w-full p-4 mt-4'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Upcoming Tasks').classes('font-bold')
                    ui.button('Add Task', on_click=lambda: show_add_task_dialog()).classes('bg-green-600 text-white text-xs')
                
                # Create a container for tasks
                with ui.column().classes('w-full gap-2 mt-2'):
                    load_tasks()

def show_day_view():
    """Show day view calendar"""
    today = datetime.now()
    day_str = today.strftime("%A, %B %d")
    
    ui.label(day_str).classes('text-sm font-semibold mb-2')
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, description, priority, 
                   TIME_FORMAT(due_time, '%H:%i') as due_time, 
                   DATE(due_date) as due_date 
            FROM tasks 
            WHERE user_id = %s AND due_date = %s
            ORDER BY due_time
        """, (1, today.date()))
        tasks = cursor.fetchall()
        cursor.close()
        
        # Time slots
        with ui.column().classes('w-full border rounded'):
            for hour in range(8, 21):
                time_str = f"{hour}:00" if hour <= 12 else f"{hour-12}:00 PM"
                with ui.row().classes('w-full p-2 border-b hover:bg-gray-50'):
                    ui.label(time_str).classes('w-20 text-xs text-gray-600')
                    with ui.column().classes('flex-grow'):
                        # Find tasks for this hour
                        hour_tasks = [task for task in tasks if task['due_time'] and int(task['due_time'].split(':')[0]) == hour]
                        for task in hour_tasks:
                            priority_color = {
                                'High': 'bg-red-100',
                                'Medium': 'bg-orange-100',
                                'Low': 'bg-blue-100'
                            }
                            with ui.card().classes(f"{priority_color[task['priority']]} p-2 text-sm mb-1"):
                                ui.label(task['title']).classes('font-semibold')
                                if task['due_time']:
                                    # Convert 24-hour format to 12-hour format
                                    time_parts = task['due_time'].split(':')
                                    hour = int(time_parts[0])
                                    minute = time_parts[1]
                                    am_pm = "AM" if hour < 12 else "PM"
                                    hour = hour if hour <= 12 else hour - 12
                                    ui.label(f"{hour}:{minute} {am_pm}").classes('text-xs')
                                else:
                                    ui.label('No time set').classes('text-xs')
    except Exception as e:
        ui.notify(f"Error loading day view: {str(e)}", color='negative')

def show_week_view():
    """Show week view calendar"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, description, priority, 
                   TIME_FORMAT(due_time, '%H:%i') as due_time, 
                   DATE(due_date) as due_date 
            FROM tasks 
            WHERE user_id = %s AND due_date BETWEEN %s AND %s
            ORDER BY due_date, due_time
        """, (1, start_of_week.date(), (start_of_week + timedelta(days=6)).date()))
        tasks = cursor.fetchall()
        cursor.close()
        
        # Week header
        with ui.row().classes('w-full gap-1'):
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                current_date = start_of_week + timedelta(days=i)
                date_str = current_date.strftime("%d")
                with ui.column().classes('flex-grow text-center p-2'):
                    ui.label(day).classes('font-semibold text-sm')
                    ui.label(date_str).classes('text-xs')
        
        # Week grid
        with ui.row().classes('w-full gap-1 mt-2'):
            for i in range(7):
                current_date = start_of_week + timedelta(days=i)
                day_tasks = [task for task in tasks if task['due_date'] == current_date.date()]
                
                with ui.column().classes('flex-grow border rounded p-1 min-h-40'):
                    for task in day_tasks:
                        priority_color = {
                            'High': 'bg-red-100',
                            'Medium': 'bg-orange-100',
                            'Low': 'bg-blue-100'
                        }
                        with ui.card().classes(f"{priority_color[task['priority']]} p-1 text-xs mb-1"):
                            ui.label(task['title']).classes('font-semibold')
                            # Check if due_time is not None before formatting
                            if task['due_time']:
                                # Convert 24-hour format to 12-hour format
                                time_parts = task['due_time'].split(':')
                                hour = int(time_parts[0])
                                minute = time_parts[1]
                                am_pm = "AM" if hour < 12 else "PM"
                                hour = hour if hour <= 12 else hour - 12
                                ui.label(f"{hour}:{minute} {am_pm}").classes('text-xs')
                            else:
                                ui.label('No time set').classes('text-xs')
    except Exception as e:
        ui.notify(f"Error loading week view: {str(e)}", color='negative')

def show_month_view():
    """Show month view calendar"""
    today = datetime.now()
    month_str = today.strftime("%B %Y")
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE user_id = %s AND MONTH(due_date) = %s AND YEAR(due_date) = %s
            ORDER BY due_date, due_time
        """, (1, today.month, today.year))
        tasks = cursor.fetchall()
        cursor.close()
        
        ui.label(month_str).classes('text-sm font-semibold text-center mb-2')
        
        # Days of week header
        with ui.row().classes('w-full'):
            for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                ui.label(day).classes('flex-grow text-center text-xs font-semibold')
        
        # Month grid
        with ui.column().classes('w-full gap-1'):
            for week in range(5):
                with ui.row().classes('w-full gap-1'):
                    for day in range(7):
                        day_num = week * 7 + day - 3  # Adjust offset for current month
                        if 1 <= day_num <= 30:
                            current_date = today.replace(day=day_num)
                            day_tasks = [task for task in tasks if task['due_date'].day == day_num]
                            
                            with ui.card().classes('flex-grow aspect-square p-1 text-center'):
                                ui.label(str(day_num)).classes('text-xs')
                                for task in day_tasks:
                                    priority_color = {
                                        'High': 'text-red-600',
                                        'Medium': 'text-orange-600',
                                        'Low': 'text-blue-600'
                                    }
                                    ui.icon('assignment').classes(f"text-xs {priority_color[task['priority']]}")
                        else:
                            ui.card().classes('flex-grow aspect-square bg-gray-100')
    except Exception as e:
        ui.notify(f"Error loading month view: {str(e)}", color='negative')

def load_tasks():
    """Load tasks from database"""
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE user_id = %s 
            ORDER BY due_date, due_time
        """, (1,))
        tasks = cursor.fetchall()
        cursor.close()
        
        # Create a new container for tasks
        with ui.column().classes('w-full gap-2 mt-2') as container:
            for task in tasks:
                task_id = task['id']  # Store task_id in a variable to avoid closure issues
                with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 rounded'):
                    ui.checkbox(value=task['status'] == 'completed', 
                              on_change=lambda e, task_id=task_id: complete_task(task_id, e.value)).classes('mr-2')
                    with ui.column().classes('flex-grow'):
                        ui.label(task['title']).classes('text-sm font-semibold')
                        if task['description']:
                            ui.label(task['description']).classes('text-xs text-gray-600')
                        ui.label(f"Due: {task['due_date']} {task['due_time']}").classes('text-xs text-gray-600')
                    priority_color = {
                        'High': 'text-red-600',
                        'Medium': 'text-orange-600',
                        'Low': 'text-blue-600'
                    }
                    ui.label(f"Priority: {task['priority']}").classes(f"text-xs {priority_color[task['priority']]}")
                    ui.button(icon='delete', on_click=lambda task_id=task_id: delete_task(task_id)).classes('text-red-600')
    except Exception as e:
        ui.notify(f"Error loading tasks: {str(e)}", color='negative')
        print(f"Database error: {str(e)}")  # For debugging

def show_add_task_dialog():
    """Show dialog to add a new task"""
    with ui.dialog() as dialog, ui.card().classes('p-4 w-96'):
        ui.label('Add New Task').classes('text-lg font-bold mb-4')
        
        task_title = ui.input('Task Title').classes('w-full mb-2')
        task_description = ui.textarea('Description').classes('w-full mb-2')
        
        with ui.row().classes('gap-2 w-full'):
            due_date = ui.date().classes('flex-grow')
            due_time = ui.time().classes('w-32')
            
        # Create a row for priority selection
        with ui.row().classes('w-full mt-2'):
            ui.label('Priority:').classes('mr-2')
            priority = ui.radio(['High', 'Medium', 'Low'], value='Medium').props('inline')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Save Task', on_click=lambda: save_task(
                task_title.value,
                due_date.value,
                due_time.value,
                priority.value,
                task_description.value,
                dialog
            )).classes('bg-green-600 text-white')
    
    dialog.open()

def save_task(title, due_date, due_time, priority, description, dialog):
    """Save a new task to the database"""
    if not title:
        ui.notify('Task title is required', color='warning')
        return
        
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, due_date, due_time, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (1, title, description, due_date, due_time, priority, 'pending'))
        db.connection.commit()
        cursor.close()
        
        ui.notify(f'Task "{title}" added successfully', color='positive')
        dialog.close()
        load_tasks()  # Refresh the task list
    except Exception as e:
        ui.notify(f"Error saving task: {str(e)}", color='negative')
        print(f"Database error: {str(e)}")  # For debugging

def complete_task(task_id, completed):
    """Update task completion status"""
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET status = %s 
            WHERE id = %s
        """, ('completed' if completed else 'pending', task_id))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Task status updated', color='positive')
    except Exception as e:
        ui.notify(f"Error updating task: {str(e)}", color='negative')

def delete_task(task_id):
    """Delete a task"""
    try:
        cursor = db.connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Task deleted', color='positive')
        load_tasks()  # Refresh the task list
    except Exception as e:
        ui.notify(f"Error deleting task: {str(e)}", color='negative') 