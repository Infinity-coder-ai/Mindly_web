from nicegui import ui
import time
from datetime import datetime

# Try to import FirebaseManager, but don't fail if it's not available
try:
    from firebase_manager import FirebaseManager
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase module not available. Chat functionality will be limited.")

class ChatInterface:
    def __init__(self):
        self.firebase = FirebaseManager() if FIREBASE_AVAILABLE else None
        self.current_user = None
        self.current_chat = None
        self.message_container = None
        self.friends_list = None
        self.chat_input = None
        self.setup_ui()

    def setup_ui(self):
        with ui.card().classes('w-full h-full'):
            with ui.row().classes('w-full h-full'):
                # Left sidebar with friends list
                with ui.column().classes('w-1/4 border-r p-4'):
                    ui.label('Friends').classes('text-xl font-bold mb-4')
                    self.friends_list = ui.column().classes('w-full')
                    with ui.row().classes('w-full mt-4'):
                        self.friend_email = ui.input(placeholder='Friend\'s email').classes('flex-grow')
                        ui.button('Add Friend', on_click=self.add_friend).classes('ml-2')
                
                # Right side chat area
                with ui.column().classes('w-3/4 p-4'):
                    self.chat_header = ui.label('Select a friend to start chatting').classes('text-xl font-bold mb-4')
                    self.message_container = ui.column().classes('w-full flex-grow overflow-y-auto')
                    with ui.row().classes('w-full mt-4'):
                        self.chat_input = ui.input(placeholder='Type a message...').classes('flex-grow')
                        ui.button('Send', on_click=self.send_message).classes('ml-2')
            
            # Show warning if Firebase is not available
            if not FIREBASE_AVAILABLE:
                with ui.dialog() as dialog, ui.card():
                    ui.label('Firebase Not Available').classes('text-xl font-bold mb-4')
                    ui.label('The chat functionality requires Firebase to be properly configured. Please check your Firebase credentials and restart the application.').classes('mb-4')
                    ui.button('OK', on_click=dialog.close).classes('w-full')

    def show_auth_dialog(self):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Authentication is disabled.', type='negative')
            return
            
        with ui.dialog() as dialog, ui.card():
            ui.label('Login or Sign Up').classes('text-xl font-bold mb-4')
            email = ui.input(placeholder='Email').classes('w-full mb-2')
            password = ui.input(placeholder='Password', password=True).classes('w-full mb-4')
            
            with ui.row().classes('w-full justify-between'):
                ui.button('Login', on_click=lambda: self.handle_login(email.value, password.value, dialog)).classes('flex-grow mr-2')
                ui.button('Sign Up', on_click=lambda: self.handle_signup(email.value, password.value, dialog)).classes('flex-grow ml-2')

    def handle_login(self, email, password, dialog):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Authentication is disabled.', type='negative')
            return
            
        if not email or not password:
            ui.notify('Please enter both email and password', type='negative')
            return
        
        user = self.firebase.sign_in(email, password)
        if user:
            self.current_user = user
            dialog.close()
            self.refresh_friends_list()
            ui.notify('Logged in successfully!', type='positive')
        else:
            ui.notify('Invalid email or password', type='negative')

    def handle_signup(self, email, password, dialog):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Authentication is disabled.', type='negative')
            return
            
        if not email or not password:
            ui.notify('Please enter both email and password', type='negative')
            return
        
        user = self.firebase.sign_up(email, password)
        if user:
            self.current_user = user
            dialog.close()
            self.refresh_friends_list()
            ui.notify('Account created successfully!', type='positive')
        else:
            ui.notify('Error creating account', type='negative')

    def add_friend(self):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Adding friends is disabled.', type='negative')
            return
            
        if not self.current_user:
            self.show_auth_dialog()
            return
        
        friend_email = self.friend_email.value
        if not friend_email:
            ui.notify('Please enter friend\'s email', type='negative')
            return
        
        success, message = self.firebase.add_friend(self.current_user['localId'], friend_email)
        if success:
            ui.notify(message, type='positive')
            self.friend_email.value = ''
            self.refresh_friends_list()
        else:
            ui.notify(message, type='negative')

    def refresh_friends_list(self):
        if not FIREBASE_AVAILABLE:
            return
            
        if not self.current_user:
            return
        
        self.friends_list.clear()
        friends = self.firebase.get_friends(self.current_user['localId'])
        
        for friend in friends:
            with ui.button(friend['email'], on_click=lambda f=friend: self.open_chat(f)).classes('w-full text-left p-2 hover:bg-gray-100'):
                pass

    def open_chat(self, friend):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Chat functionality is disabled.', type='negative')
            return
            
        self.current_chat = friend
        self.chat_header.set_text(f'Chat with {friend["email"]}')
        self.refresh_messages()
        
        # Start message polling
        if hasattr(self, 'message_polling'):
            self.message_polling.cancel()
        self.message_polling = ui.timer(1.0, self.refresh_messages)

    def refresh_messages(self):
        if not FIREBASE_AVAILABLE:
            return
            
        if not self.current_user or not self.current_chat:
            return
        
        self.message_container.clear()
        messages = self.firebase.get_messages(self.current_user['localId'], self.current_chat['id'])
        
        for msg in messages:
            is_own = msg['sender_id'] == self.current_user['localId']
            with ui.row().classes(f'w-full {"justify-end" if is_own else "justify-start"} mb-2'):
                with ui.card().classes(f'{"bg-blue-100" if is_own else "bg-gray-100"} p-2 max-w-[70%]'):
                    ui.label(msg['message'])
                    ui.label(datetime.fromtimestamp(msg['timestamp'].timestamp()).strftime('%H:%M')).classes('text-xs text-gray-500')

    def send_message(self):
        if not FIREBASE_AVAILABLE:
            ui.notify('Firebase is not available. Sending messages is disabled.', type='negative')
            return
            
        if not self.current_user or not self.current_chat:
            ui.notify('Please select a friend to chat with', type='negative')
            return
        
        message = self.chat_input.value
        if not message:
            return
        
        if self.firebase.send_message(self.current_user['localId'], self.current_chat['id'], message):
            self.chat_input.value = ''
            self.refresh_messages()
        else:
            ui.notify('Error sending message', type='negative') 