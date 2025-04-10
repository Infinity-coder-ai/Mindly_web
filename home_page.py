from nicegui import ui
from datetime import datetime
import time
import random

class HomePage:
    def __init__(self, username):
        self.username = username
        self.timer_running = False
        self.timer_start_time = None
        self.timer_interval = None
        self.background_images = [
            'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80',
            'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80',
            'https://images.unsplash.com/photo-1509062522246-3755977927d7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80'
        ]
        
        # Page is already cleared by ui.clear() in the route handler
        
        self.setup_styles()
        self.create_home_page()

    def setup_styles(self):
        selected_background = random.choice(self.background_images)
        ui.add_head_html(f'''
        <style>
            .home-container {{
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                display: flex;
                overflow: auto;
                opacity: 0.9;
                height: 100vh;
                width: 100vw;
                z-index: 1000;
            }}

            .sidebar {{
                position: fixed;
                left: -300px;
                top: 0;
                bottom: 0;
                width: 300px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                transition: left 0.3s ease;
                z-index: 1100;
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
                padding: 1rem;
            }}

            .sidebar.open {{
                left: 0;
            }}

            .main-content {{
                flex: 1;
                padding: 3rem;
                margin-left: 0;
                transition: margin-left 0.3s ease;
                z-index: 1000;
            }}

            .main-content.sidebar-open {{
                margin-left: 300px;
            }}

            .title-container {{
                text-align: center;
                margin-bottom: 4rem;
            }}

            .main-title {{
                font-size: 4rem;
                font-weight: bold;
                color: #fff;
                text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.5);
                margin-bottom: 1.5rem;
                animation: fadeInDown 1s ease-out;
            }}

            .subtitle {{
                font-size: 1.8rem;
                color: #fff;
                text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
                animation: fadeInUp 1s ease-out;
            }}

            .feature-button {{
                background: #4FC3F7;
                color: white;
                border: none;
                padding: 1.2rem 2.5rem;
                border-radius: 20px;
                font-weight: bold;
                transition: all 0.3s ease;
                margin: 1rem 0;
                min-width: 250px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .feature-button:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            }}

            .feature-button:active {{
                transform: translateY(0);
            }}

            .dropdown-menu {{
                position: absolute;
                top: 100%;
                left: 0;
                background: white;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                padding: 0.5rem;
                display: none;
                z-index: 1200;
                width: 100%;
            }}

            .dropdown-menu.show {{
                display: block;
                animation: fadeIn 0.3s ease-out;
            }}

            .dropdown-item {{
                background: #4FC3F7;
                color: white;
                padding: 0.8rem 1.5rem;
                cursor: pointer;
                transition: all 0.2s ease;
                border-radius: 5px;
                width: 100%;
                text-align: left;
                margin: 0.2rem 0;
            }}

            .dropdown-item:hover {{
                background: #3daee9;
            }}

            .menu-toggle {{
                position: fixed;
                left: 20px;
                top: 20px;
                z-index: 1300;
                background: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .menu-toggle:hover {{
                transform: scale(1.1);
            }}

            .clock {{
                font-size: 2.2rem;
                font-weight: bold;
                color: #333;
                text-align: center;
                margin: 1.5rem 0;
            }}

            .calendar {{
                background: white;
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}

            .calendar-day {{
                width: 45px;
                height: 45px;
                padding: 0;
                margin: 2px;
                font-size: 1rem;
            }}

            .calendar-day.marked {{
                background: #2196F3;
                color: white;
            }}

            .timer {{
                text-align: center;
                margin: 1.5rem 0;
            }}

            .timer-display {{
                font-size: 2.5rem;
                font-weight: bold;
                color: #333;
            }}

            .timer-button {{
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.7rem 1.5rem;
                margin: 0.3rem;
                cursor: pointer;
                transition: all 0.2s ease;
            }}

            .timer-button:hover {{
                background: #1976D2;
            }}

            .timer-button.stop {{
                background: #f44336;
            }}

            .timer-button.stop:hover {{
                background: #d32f2f;
            }}

            .timer-button.reset {{
                background: #757575;
            }}

            .timer-button.reset:hover {{
                background: #616161;
            }}

            .feature-icon {{
                font-size: 1.8rem;
                margin-right: 0.8rem;
                animation: pulse 2s infinite;
                color: white;
            }}

            @keyframes fadeInDown {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}

            @keyframes bounce {{
                0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                40% {{ transform: translateY(-10px); }}
                60% {{ transform: translateY(-5px); }}
            }}

            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.2); }}
                100% {{ transform: scale(1); }}
            }}

            .bounce {{
                animation: bounce 1s;
            }}
        </style>
        ''')

    def create_home_page(self):
        # Use a single top-level container for the home page
        # This ensures that NiceGUI replaces all content properly
        with ui.element('div').style('position: fixed; top: 0; left: 0; width: 100%; height: 100vh; z-index: 1000;'):
            with ui.column().classes('home-container'):
                # Sidebar Toggle Button with Animated Icon
                with ui.button(icon='menu').classes('menu-toggle') as menu_btn:
                    menu_btn.on('click', self.toggle_sidebar)

                # Sidebar
                with ui.column().classes('sidebar') as sidebar:
                    with ui.column().classes('p-4'):
                        ui.label(f'Welcome, {self.username}!').classes('text-h6 q-mb-md')
                        # Clock
                        self.clock_label = ui.label().classes('clock')
                        self.update_clock()

                        # Calendar
                        with ui.card().classes('calendar w-full'):
                            ui.label('Calendar').classes('text-h6')
                            with ui.grid(columns=7).classes('w-full'):
                                for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                                    ui.label(day).classes('text-center text-caption')
                                self.calendar_days = []
                                for i in range(35):
                                    btn = ui.button(str(i + 1), on_click=lambda e, num=i+1: self.toggle_mark(num)).classes('calendar-day')
                                    self.calendar_days.append(btn)

                        # Timer
                        with ui.card().classes('timer w-full'):
                            ui.label('Timer').classes('text-h6')
                            self.timer_display = ui.label('00:00:00').classes('timer-display')
                            with ui.row().classes('w-full justify-center gap-2'):
                                ui.button('Start', on_click=self.start_timer).classes('timer-button')
                                ui.button('Stop', on_click=self.stop_timer).classes('timer-button stop')
                                ui.button('Reset', on_click=self.reset_timer).classes('timer-button reset')

                # Main Content
                with ui.column().classes('main-content') as main_content:
                    # Title Section
                    with ui.column().classes('title-container'):
                        ui.html('<div class="main-title">Mindly</div>')
                        ui.html('<div class="subtitle">e-learning website</div>')

                    # Navigation Bar
                    with ui.row().classes('nav-container'):
                        # Logo
                        with ui.row().classes('logo'):
                            ui.icon('school').classes('text-2xl')
                            ui.label('Mindly').classes('logo-text')
                        
                        # Navigation Links
                        with ui.row().classes('nav-links'):
                            ui.button('PDF Listener', on_click=lambda: self.handle_nav_click('PDF Listener')).classes('nav-link')
                            
                            # Recording and Planning with dropdown
                            with ui.button('Recording & Planning', on_click=lambda: self.toggle_nav_dropdown('planning')).classes('nav-link relative'):
                                ui.icon('expand_more').classes('text-sm')
                            with ui.menu(close_on_click=True).classes('bg-white rounded-lg shadow-lg').id('planning-dropdown'):
                                ui.menu_item('Study Planner', on_click=lambda: self.handle_nav_dropdown_click('Study Planner')).classes('px-4 py-2 hover:bg-gray-100')
                                ui.menu_item('Reminders', on_click=lambda: self.handle_nav_dropdown_click('Reminders')).classes('px-4 py-2 hover:bg-gray-100')
                            
                            ui.button('Chatroom', on_click=lambda: self.handle_nav_click('Chatroom')).classes('nav-link')
                            
                            # Take Notes with dropdown
                            with ui.button('Take Notes', on_click=lambda: self.toggle_nav_dropdown('notes')).classes('nav-link relative'):
                                ui.icon('expand_more').classes('text-sm')
                            with ui.menu(close_on_click=True).classes('bg-white rounded-lg shadow-lg').id('notes-dropdown'):
                                ui.menu_item('Flash Card', on_click=lambda: self.handle_nav_dropdown_click('Flash Card')).classes('px-4 py-2 hover:bg-gray-100')
                                ui.menu_item('Essays', on_click=lambda: self.handle_nav_dropdown_click('Essays')).classes('px-4 py-2 hover:bg-gray-100')
                        
                        # Find A Tutor Button and Logout
                        with ui.row().classes('gap-2'):
                            ui.button('Find A Tutor', on_click=lambda: self.handle_nav_click('Find A Tutor')).classes('find-tutor-btn')
                            ui.button('Logout', on_click=self.logout).classes('find-tutor-btn bg-red-500 hover:bg-red-600')

    def toggle_sidebar(self):
        sidebar = ui.query('.sidebar')
        main_content = ui.query('.main-content')
        if 'open' in sidebar.classes:
            sidebar.classes.remove('open')
            main_content.classes.remove('sidebar-open')
        else:
            sidebar.classes.add('open')
            main_content.classes.add('sidebar-open')

    def toggle_planning_menu(self):
        planning_menu = ui.query('.feature-button:nth-child(2) .dropdown-menu')
        planning_menu.classes.toggle('show')
        notes_menu = ui.query('.feature-button:nth-child(4) .dropdown-menu')
        notes_menu.classes.remove('show')

    def toggle_notes_menu(self):
        notes_menu = ui.query('.feature-button:nth-child(4) .dropdown-menu')
        notes_menu.classes.toggle('show')
        planning_menu = ui.query('.feature-button:nth-child(2) .dropdown-menu')
        planning_menu.classes.remove('show')

    def handle_feature_click(self, feature):
        ui.notify(f'Feature clicked: {feature}')
        button = ui.query(f'.feature-button:contains("{feature}")')
        button.classes.add('bounce')
        ui.timer(1.0, lambda: button.classes.remove('bounce'))

    def handle_menu_click(self, option):
        ui.notify(f'Selected: {option}')
        button = ui.query(f'.dropdown-item:contains("{option}")')
        button.classes.add('bounce')
        ui.timer(1.0, lambda: button.classes.remove('bounce'))
        ui.query('.dropdown-menu').classes.remove('show')

    def toggle_mark(self, day):
        button = self.calendar_days[day - 1]
        if 'marked' in button.classes:
            button.classes.remove('marked')
        else:
            button.classes.add('marked')

    def update_clock(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.clock_label.set_text(current_time)
        ui.timer(1.0, self.update_clock)

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_start_time = time.time()
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_interval:
            self.timer_interval.cancel()

    def reset_timer(self):
        self.timer_running = False
        if self.timer_interval:
            self.timer_interval.cancel()
        self.timer_display.set_text('00:00:00')

    def update_timer(self):
        if self.timer_running:
            elapsed = time.time() - self.timer_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.timer_display.set_text(f'{hours:02d}:{minutes:02d}:{seconds:02d}')
            self.timer_interval = ui.timer(1.0, self.update_timer)

    def logout(self):
        """Handle logout and redirect to login page"""
        ui.notify('Logging out...', type='info')
        # Use navigate.to with a slight delay to ensure notification is shown
        ui.timer(0.8, lambda: ui.navigate.to('/'))