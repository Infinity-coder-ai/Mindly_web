from nicegui import ui, app
from datetime import datetime, timedelta
import asyncio
import threading
import time
from typing import Dict, Optional

class TimerManager:
    def __init__(self):
        self.timers: Dict[int, dict] = {}
        self.timer_id_counter = 0
        self._running = True
        # Start background thread to check timers
        self.thread = threading.Thread(target=self._check_timers_thread, daemon=True)
        self.thread.start()
    
    def start_timer(self, minutes: int, description: str = "Timer") -> int:
        """Start a new timer and return its ID"""
        timer_id = self.timer_id_counter
        self.timer_id_counter += 1
        
        end_time = datetime.now() + timedelta(minutes=minutes)
        
        self.timers[timer_id] = {
            'end_time': end_time,
            'description': description,
            'minutes': minutes,
            'notified': False
        }
        
        return timer_id
    
    def cancel_timer(self, timer_id: int) -> bool:
        """Cancel a timer by ID, return True if successful"""
        if timer_id in self.timers:
            del self.timers[timer_id]
            return True
        return False
    
    def get_remaining_time(self, timer_id: int) -> Optional[timedelta]:
        """Get remaining time for a timer"""
        if timer_id in self.timers:
            now = datetime.now()
            end_time = self.timers[timer_id]['end_time']
            if now < end_time:
                return end_time - now
            return timedelta(0)
        return None
    
    def get_active_timers(self):
        """Get all active timers with remaining time"""
        now = datetime.now()
        active_timers = {}
        for timer_id, timer in list(self.timers.items()):
            if now < timer['end_time']:
                remaining = timer['end_time'] - now
                active_timers[timer_id] = {
                    'description': timer['description'],
                    'minutes': timer['minutes'],
                    'remaining_seconds': remaining.total_seconds(),
                    'remaining_formatted': f"{int(remaining.total_seconds() // 60):02d}:{int(remaining.total_seconds() % 60):02d}"
                }
            elif not timer['notified']:
                # Mark as notified to prevent multiple notifications
                self.timers[timer_id]['notified'] = True
                # Show notification for completed timer - Use a different approach
                ui.timer(0, lambda tid=timer_id, desc=timer['description']: 
                    self.show_completed_notification(tid, desc))
                
                # Keep expired timers until they're acknowledged
                active_timers[timer_id] = {
                    'description': timer['description'],
                    'minutes': timer['minutes'],
                    'remaining_seconds': 0,
                    'remaining_formatted': "00:00",
                    'completed': True
                }
        return active_timers
    
    def shutdown(self):
        """Stop the timer checking thread"""
        self._running = False
        if self.thread.is_alive():
            self.thread.join(1.0)  # Wait for thread to end
    
    def _check_timers_thread(self):
        """Background thread to periodically check timers"""
        while self._running:
            # Just sleep - the actual checking happens when get_active_timers is called
            time.sleep(0.5)
    
    def show_completed_notification(self, timer_id, description):
        """Show notification directly (not as async method)"""
        # Use a class variable to track if a notification is already showing
        if not hasattr(self, '_notification_showing'):
            self._notification_showing = False
        
        # If a notification is already showing, don't create another one
        if self._notification_showing:
            return
        
        # Set the flag to indicate a notification is showing
        self._notification_showing = True
        
        # Play sound
        ui.run_javascript("""
        try {
            const audio = new Audio('/static/notification.mp3');
            audio.volume = 1.0;
            audio.play();
        } catch(e) {
            console.error('Error playing sound:', e);
        }
        """)
        
        # Show browser notification
        ui.run_javascript(f"""
        if ('Notification' in window && Notification.permission === 'granted') {{
            new Notification('Timer Complete: {description}', {{
                icon: '/static/alarm-icon.png',
                body: 'Your timer has finished!'
            }});
        }}
        """)
        
        # Create a dialog for notification
        dialog = ui.dialog().classes('notification-dialog')
        
        with dialog, ui.card().classes('p-6 text-center'):
            ui.icon('alarm').classes('text-6xl text-green-600 mb-4')
            ui.label(f'Timer Complete!').classes('text-2xl font-bold mb-2')
            ui.label(f'{description}').classes('text-lg mb-4')
            
            # Create a function to close dialog and reset flag
            def close_dialog():
                self._notification_showing = False
                dialog.close()
            
            # Use a separate JavaScript function to hide dialog UI elements
            def handle_dismiss():
                ui.run_javascript("""
                    document.querySelector('.notification-dialog').style.display = 'none';
                    document.querySelector('.notification-dialog').classList.remove('visible');
                """)
                close_dialog()
            
            # Add the dismiss button with the proper handler
            ui.button('DISMISS', on_click=handle_dismiss).classes('bg-green-600 text-white')
        
        # Open the dialog
        dialog.open()

# Global timer manager instance
timer_manager = TimerManager()

# Store timer manager in app.storage directly (no need for startup handler)
app.storage.timer_manager = timer_manager

def create_timer_ui(container):
    """Create timer UI in the provided container"""
    # Request notification permission on page load
    ui.run_javascript("""
    if ('Notification' in window) {
        if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
            Notification.requestPermission();
        }
    }
    """)
    
    with container:
        ui.label('Timer').classes('text-xl font-semibold mb-2')
        
        with ui.row().classes('w-full items-center'):
            minutes = ui.number('Minutes', value=0.1).classes('w-32')  # Set to 0.1 for testing
            description = ui.input('Description', value='Study Session').classes('flex-grow')
        
        with ui.row().classes('w-full gap-2 mt-2'):
            ui.button('Start Timer', icon='play_arrow', on_click=lambda: start_new_timer(
                minutes.value, description.value, timer_elements
            )).classes('bg-green-600 text-white')
        
        # Container for active timers
        timers_container = ui.column().classes('w-full mt-4 gap-2')
        
        # Dictionary to keep track of timer UI elements
        timer_elements = {}
        
        # Update timer display every second
        def update_timers():
            active_timers = timer_manager.get_active_timers()
            
            # Remove UI elements for timers that are no longer active
            timer_ids_to_remove = []
            for timer_id in list(timer_elements.keys()):
                if timer_id not in active_timers:
                    timer_ids_to_remove.append(timer_id)
            
            for timer_id in timer_ids_to_remove:
                timer_elements[timer_id]['container'].delete()
                del timer_elements[timer_id]
            
            # Update existing timers and create new ones
            for timer_id, timer in active_timers.items():
                if timer_id in timer_elements:
                    # Update existing timer display
                    elements = timer_elements[timer_id]
                    
                    if timer.get('completed', False):
                        elements['time_label'].set_text('Completed!')
                        elements['time_label'].classes(replace='text-green-600 font-bold')
                    else:
                        elements['time_label'].set_text(timer['remaining_formatted'])
                    
                    progress_value = 100 - (timer['remaining_seconds'] / (timer['minutes'] * 60) * 100)
                    progress_value = min(max(progress_value, 0), 100)  # Ensure value is between 0 and 100
                    elements['progress'].set_value(progress_value/100)
                else:
                    # Create new timer display
                    with timers_container:
                        with ui.card().classes('w-full p-3') as card:
                            with ui.row().classes('w-full items-center justify-between'):
                                ui.label(timer['description']).classes('font-bold')
                                time_label = ui.label(timer['remaining_formatted']).classes('font-mono text-lg')
                                if timer.get('completed', False):
                                    time_label.set_text('Completed!')
                                    time_label.classes(replace='text-green-600 font-bold')
                            
                            progress_value = 100 - (timer['remaining_seconds'] / (timer['minutes'] * 60) * 100)
                            progress_value = min(max(progress_value, 0), 100)  # Ensure value is between 0 and 100
                            progress = ui.linear_progress(value=progress_value/100).classes('w-full')
                            
                            with ui.row().classes('w-full justify-end mt-2'):
                                cancel_btn = ui.button(
                                    'Cancel', 
                                    icon='close', 
                                    on_click=lambda tid=timer_id: cancel_timer(tid, timer_elements)
                                ).classes('text-red-600').props('flat')
                            
                            # Store references to the UI elements for this timer
                            timer_elements[timer_id] = {
                                'container': card,
                                'time_label': time_label,
                                'progress': progress,
                                'cancel_btn': cancel_btn
                            }
        
        # Update timer display initially and every second
        update_timers()
        ui.timer(1.0, update_timers)

def start_new_timer(minutes, description, timer_elements=None):
    """Start a new timer with the given duration and description"""
    if not minutes or minutes <= 0:
        ui.notify('Please enter a valid duration', color='warning')
        return
    
    timer_manager.start_timer(minutes, description)
    ui.notify(f'Timer started: {description} for {minutes} minutes', color='positive')

def cancel_timer(timer_id, timer_elements=None):
    """Cancel a timer by ID"""
    if timer_manager.cancel_timer(timer_id):
        ui.notify('Timer canceled', color='warning')
        
        # Remove the UI element if it exists
        if timer_elements and timer_id in timer_elements:
            timer_elements[timer_id]['container'].delete()
            del timer_elements[timer_id]
    else:
        ui.notify('Failed to cancel timer', color='negative')

# Register cleanup function directly for atexit instead of using app.on_shutdown
import atexit
atexit.register(timer_manager.shutdown) 