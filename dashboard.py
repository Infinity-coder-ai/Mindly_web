from nicegui import ui
from datetime import datetime, timedelta
import asyncio
import math
import time
from timer_manager import timer_manager, create_timer_ui

def show_dashboard(container):
    """Display the dashboard with courses and statistics"""
    
    # Add custom CSS for the dashboard
    ui.add_head_html('''
    <style>
        .dashboard-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .widget-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .widget-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }
        
        .animation-icon {
            width: 100px;
            height: 100px;
            margin: 0 auto;
            background: url('https://example.com/animation-icon.gif') no-repeat center center;
            background-size: contain;
        }
        
        .analog-clock {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 0 auto;
            background: white;
            border-radius: 50%;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .clock-face {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid #f0f0f0;
        }
        
        .clock-hour, .clock-minute, .clock-second {
            position: absolute;
            top: 50%;
            left: 50%;
            transform-origin: 50% 0%;
        }
        
        .clock-hour {
            width: 6px;
            height: 60px;
            margin-left: -3px;
            background: #333;
            border-radius: 6px;
        }
        
        .clock-minute {
            width: 4px;
            height: 80px;
            margin-left: -2px;
            background: #666;
            border-radius: 4px;
        }
        
        .clock-second {
            width: 2px;
            height: 90px;
            margin-left: -1px;
            background: #e91e63;
            border-radius: 2px;
        }
        
        .clock-center {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            margin-top: -6px;
            margin-left: -6px;
            background: #e91e63;
            border-radius: 50%;
        }
        
        .calendar-day {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .calendar-day:hover {
            background-color: #f0f0f0;
        }
        
        .calendar-day.marked {
            background-color: rgba(33, 150, 243, 0.2);
            color: #2196F3;
            font-weight: bold;
        }
        
        .timer-controls {
            display: flex;
            gap: 8px;
            justify-content: center;
            margin-top: 12px;
        }
        
        .stat-card {
            background: linear-gradient(45deg, #4b6cb7 0%, #182848 100%);
            color: white;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: scale(1.05);
        }
    </style>
    ''')
    
    # Add JavaScript for the analog clock
    ui.add_head_html('''
    <script>
        function updateAnalogClock() {
            const now = new Date();
            const hours = now.getHours() % 12;
            const minutes = now.getMinutes();
            const seconds = now.getSeconds();
            
            const hourHand = document.querySelector('.clock-hour');
            const minuteHand = document.querySelector('.clock-minute');
            const secondHand = document.querySelector('.clock-second');
            
            if (hourHand && minuteHand && secondHand) {
                const hourDeg = (hours * 30) + (0.5 * minutes);
                const minuteDeg = (minutes * 6) + (0.1 * seconds);
                const secondDeg = seconds * 6;
                
                hourHand.style.transform = `translateY(-50%) rotate(${hourDeg}deg)`;
                minuteHand.style.transform = `translateY(-50%) rotate(${minuteDeg}deg)`;
                secondHand.style.transform = `translateY(-50%) rotate(${secondDeg}deg)`;
            }
        }
        
        // Update clock every second
        setInterval(updateAnalogClock, 1000);
        
        // Initial update
        document.addEventListener('DOMContentLoaded', updateAnalogClock);
    </script>
    ''')
    
    # Add notification sound
    ui.add_head_html('''
    <audio id="notification-sound" preload="auto">
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    <script>
        // Initialize audio
        document.addEventListener('DOMContentLoaded', function() {
            window.notificationAudio = document.getElementById('notification-sound');
            
            // Initialize on first user interaction
            document.addEventListener('click', function initAudio() {
                if (window.notificationAudio) {
                    window.notificationAudio.volume = 0.01;
                    window.notificationAudio.play().then(() => {
                        window.notificationAudio.pause();
                        window.notificationAudio.volume = 1.0;
                        console.log('Notification audio initialized');
                    }).catch(e => console.error('Audio init failed:', e));
                    document.removeEventListener('click', initAudio);
                }
            });
        });
        
        function playNotificationSound() {
            if (window.notificationAudio) {
                window.notificationAudio.currentTime = 0;
                window.notificationAudio.play().catch(e => console.error('Failed to play notification:', e));
            }
        }
    </script>
    ''')
    
    with container.classes('dashboard-container'):
        # Welcome section with current date and time
        with ui.card().classes('w-full p-4 mb-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white'):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            with ui.row().classes('w-full items-center'):
                with ui.column().classes('flex-grow'):
                    ui.label('Your Learning Dashboard').classes('text-xl font-bold mb-2')
                    time_label = ui.label(f"Today is {current_date}").classes('text-sm opacity-90')
                    
                    # Update time every second
                    async def update_time():
                        while True:
                            current_time = datetime.now().strftime("%H:%M:%S")
                            time_label.set_text(f"Today is {current_date} | Current time: {current_time}")
                            await asyncio.sleep(1)
                    
                    ui.timer(0.1, lambda: asyncio.create_task(update_time()))
                
                # Add animation icon
                with ui.column().classes('items-center'):
                    ui.element('div').classes('animation-icon')
        
        # Widgets row: Clock, Timer, Calendar
        with ui.row().classes('w-full gap-4 mb-6'):
            # Analog Clock Widget
            with ui.card().classes('flex-1 widget-card p-4'):
                ui.label('Analog Clock').classes('text-lg font-semibold mb-3 text-center')
                with ui.element('div').classes('analog-clock'):
                    ui.element('div').classes('clock-face')
                    for i in range(12):
                        hour_mark = ui.element('div').style(f'position: absolute; width: 2px; height: 15px; background: #333; top: 10px; left: 50%; margin-left: -1px; transform-origin: 50% 90px; transform: rotate({i * 30}deg);')
                    ui.element('div').classes('clock-hour')
                    ui.element('div').classes('clock-minute')
                    ui.element('div').classes('clock-second')
                    ui.element('div').classes('clock-center')
            
            # Timer Widget using the persistent timer manager
            with ui.card().classes('flex-1 widget-card p-4'):
                create_timer_ui(ui.column().classes('w-full'))
            
            # Calendar Widget
            with ui.card().classes('flex-1 widget-card p-4'):
                ui.label('Study Calendar').classes('text-lg font-semibold mb-3 text-center')
                
                today = datetime.now()
                current_year = today.year
                current_month = today.month
                
                # Month navigation
                with ui.row().classes('w-full items-center justify-between mb-3'):
                    month_label = ui.label(f"{datetime(current_year, current_month, 1).strftime('%B %Y')}").classes('text-md')
                    with ui.row().classes('gap-2'):
                        ui.button(icon='chevron_left', on_click=lambda: change_month(-1)).props('flat dense')
                        ui.button(icon='chevron_right', on_click=lambda: change_month(1)).props('flat dense')
                
                # Calendar grid container
                calendar_container = ui.column().classes('w-full')
                
                def get_month_days(year, month):
                    """Get the number of days in a month"""
                    if month == 12:
                        return (datetime(year + 1, 1, 1) - datetime(year, month, 1)).days
                    else:
                        return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
                
                def display_calendar(year, month):
                    """Display the calendar for the given month"""
                    # Update the month/year label
                    month_label.set_text(f"{datetime(year, month, 1).strftime('%B %Y')}")
                    
                    # Clear the previous calendar
                    calendar_container.clear()
                    
                    # Days of week header
                    with calendar_container:
                        with ui.row().classes('w-full mb-2'):
                            for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                                ui.label(day).classes('flex-grow text-center text-xs')
                        
                        # Calculate first day of the month (0 = Monday, 6 = Sunday)
                        first_day = datetime(year, month, 1).weekday()
                        # Adjust to Sunday = 0
                        first_day = (first_day + 1) % 7
                        
                        # Number of days in the month
                        num_days = get_month_days(year, month)
                        
                        # Calendar rows
                        current_row = ui.row().classes('w-full mb-1')
                        
                        # Empty cells for the first row
                        for _ in range(first_day):
                            with current_row:
                                ui.label('').classes('flex-grow aspect-square')
                        
                        # Days of the month
                        for day in range(1, num_days + 1):
                            if (first_day + day - 1) % 7 == 0 and day != 1:
                                current_row = ui.row().classes('w-full mb-1')
                            
                            with current_row:
                                day_element = ui.label(str(day)).classes('flex-grow text-center text-xs calendar-day aspect-square py-1')
                                if year == today.year and month == today.month and day == today.day:
                                    day_element.classes('bg-blue-100 font-bold')
                                
                                # Add click event to mark/unmark days
                                day_element.on('click', lambda e, element=day_element: toggle_mark_day(element))
                
                def toggle_mark_day(element):
                    """Toggle the marked state of a calendar day"""
                    if 'marked' in element.classes():
                        element.remove_classes('marked')
                    else:
                        element.add_classes('marked')
                
                def change_month(delta):
                    """Change the displayed month by delta"""
                    nonlocal current_year, current_month
                    
                    current_month += delta
                    if current_month > 12:
                        current_month = 1
                        current_year += 1
                    elif current_month < 1:
                        current_month = 12
                        current_year -= 1
                    
                    display_calendar(current_year, current_month)
                
                # Display the initial calendar
                display_calendar(current_year, current_month)

def get_icon_for_course(title):
    """Return the appropriate icon for a course based on its title"""
    title = title.lower()
    if 'math' in title:
        return 'functions'
    elif 'science' in title or 'chemistry' in title or 'physics' in title:
        return 'science'
    elif 'history' in title:
        return 'history_edu'
    elif 'language' in title or 'english' in title:
        return 'translate'
    elif 'computer' in title or 'programming' in title:
        return 'code'
    else:
        return get_random_course_icon()

def get_random_course_icon():
    """Return a random course icon"""
    icons = ['menu_book', 'school', 'psychology', 'biotech', 'public', 'lightbulb', 'insights']
    return icons[int(time.time()) % len(icons)] 