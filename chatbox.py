from nicegui import ui, app
from firebase_chat import get_firebase_chat
import time
from firebase_admin import auth as admin_auth
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ChatBox')

# Store references to active message listeners
message_listeners = {}
typing_listeners = {}
current_chat_friend = None
messages_content = None
messages_container = None

def show_chatbox(container):
    """Show the chat interface"""
    global messages_content, messages_container, current_chat_friend
    # Get the Firebase chat instance
    firebase_chat = get_firebase_chat()
    
    def show_welcome_message(chat_area):
        chat_area.clear()
        with chat_area:
            with ui.column().classes('w-full h-full flex items-center justify-center'):
                ui.label('👋 Welcome to Chat!').classes('text-2xl font-bold text-gray-600 mb-2')
                ui.label('Select a friend from the list to start chatting').classes('text-gray-500')
    
    def show_chat(friend_uid, chat_area):
        global current_chat_friend, messages_content, messages_container
        current_chat_friend = friend_uid
        chat_area.clear()
        
        # Get friend's data before setting up chat UI
        friend_data = None
        try:
            friends = firebase_chat.get_friends(firebase_chat.current_user['localId'])
            friend_data = next((friend for friend in friends if friend['uid'] == friend_uid), None)
        except Exception as e:
            logger.error(f"Error getting friend data: {str(e)}")
        
        friend_email = friend_data['email'] if friend_data else 'Unknown'
        
        with chat_area:
            # Chat header
            with ui.row().classes('w-full bg-blue-500 text-white p-4'):
                ui.label(f'Chat with {friend_email}').classes('text-lg font-bold')
            
            # Messages container with flex layout
            messages_wrapper = ui.column().classes('w-full h-[calc(100%-8rem)] flex flex-col')
            with messages_wrapper:
                # Messages container that scrolls
                messages_container = ui.scroll_area().classes('w-full flex-grow')
                with messages_container:
                    messages_content = ui.column().classes('w-full p-4 space-y-2')
                
                # Message input area at bottom
                with ui.row().classes('w-full p-4 bg-gray-100 gap-2'):
                    message_input = ui.input(placeholder='Type a message...').classes('flex-grow')
                    send_btn = ui.button('Send', on_click=lambda: send_message(message_input.value)).classes('bg-blue-500 text-white')
                
                def send_message(message_text):
                    try:
                        if not message_text or not message_text.strip():
                            return
                        
                        # Send message to Firebase
                        message_data = {
                            'message': message_text,
                            'timestamp': int(time.time() * 1000),  # Use milliseconds
                            'from': firebase_chat.current_user['localId']
                        }
                        
                        # Add debug logging
                        logger.debug(f"Attempting to save message: {message_data}")
                        logger.debug(f"Current user ID: {firebase_chat.current_user['localId']}")
                        logger.debug(f"Friend ID: {current_chat_friend}")
                        
                        # Save message for both users
                        firebase_chat.db.child('messages').child(firebase_chat.current_user['localId']).child(current_chat_friend).push(message_data)
                        firebase_chat.db.child('messages').child(current_chat_friend).child(firebase_chat.current_user['localId']).push(message_data)
                        
                        message_input.value = ''
                        logger.info(f"Message sent successfully to {current_chat_friend}")
                        
                        # Force refresh messages
                        refresh_messages()
                        
                    except Exception as e:
                        logger.error(f'Error sending message: {str(e)}')
                        logger.exception("Full traceback:")
                        ui.notify(f'Error sending message: {str(e)}', color='negative')
                
                def refresh_messages():
                    try:
                        if not messages_content or not current_chat_friend:
                            return
                            
                        # Clear existing messages
                        messages_content.clear()
                        
                        # Get messages from Firebase
                        messages_ref = firebase_chat.db.child('messages').child(firebase_chat.current_user['localId']).child(current_chat_friend).get()
                        messages = []
                        
                        if messages_ref and messages_ref.val():
                            for msg_key, msg_val in messages_ref.val().items():
                                messages.append({
                                    'message': msg_val.get('message', ''),
                                    'timestamp': msg_val.get('timestamp', 0),
                                    'from': msg_val.get('from', '')
                                })
                            
                            # Sort messages by timestamp
                            messages.sort(key=lambda x: x['timestamp'])
                        
                        # Clear and rebuild messages content
                        with messages_content:
                            for msg in messages:
                                is_self = msg['from'] == firebase_chat.current_user['localId']
                                with ui.row().classes(f'w-full justify-{"end" if is_self else "start"}'):
                                    with ui.card().classes(f'{"bg-blue-500 text-white" if is_self else "bg-gray-100"} p-2 rounded-lg max-w-[70%]'):
                                        ui.label(msg['message']).classes('whitespace-pre-wrap break-words')
                                        timestamp = datetime.fromtimestamp(msg['timestamp'] / 1000).strftime('%H:%M')
                                        ui.label(timestamp).classes('text-xs opacity-75 text-right')
                        
                        # Scroll to bottom after messages are loaded
                        if messages_container:
                            messages_container.scroll_to(percent=1.0)
                        
                        logger.debug(f"Refreshed {len(messages)} messages for chat with {current_chat_friend}")
                    except Exception as e:
                        logger.error(f'Error refreshing messages: {str(e)}')
                        logger.exception("Full traceback:")
                
                # Handle Enter key for sending message
                def on_key_press(e):
                    try:
                        if e.args.get('key') == 'Enter' and not e.args.get('shiftKey', False):
                            send_message(message_input.value)
                    except Exception as e:
                        logger.error(f'Error handling key press: {str(e)}')
                
                message_input.on('keydown', on_key_press)
                
                # Initial load of messages
                refresh_messages()
                
                # Set up real-time updates
                def handle_message_update(message):
                    if message and current_chat_friend:
                        with messages_container:
                            refresh_messages()
                
                # Clean up previous listener if exists
                if friend_uid in message_listeners:
                    message_listeners[friend_uid].close()
                
                # Listen for new messages
                message_listeners[friend_uid] = firebase_chat.db.child('messages').child(firebase_chat.current_user['localId']).child(friend_uid).stream(handle_message_update)
    
    def refresh_friends_list(friends_list, chat_area):
        try:
            friends_list.clear()
            friends = firebase_chat.get_friends(firebase_chat.current_user['localId'])
            for friend in friends:
                with ui.card().classes('w-full cursor-pointer hover:bg-gray-100 mb-2').on('click', lambda f=friend: show_chat(f['uid'], chat_area)):
                    with ui.row().classes('w-full items-center p-2'):
                        # Friend avatar
                        ui.icon('person').classes('text-2xl text-gray-600')
                        # Friend info
                        with ui.column().classes('flex-grow ml-2'):
                            ui.label(friend['email']).classes('font-bold')
                            status = 'Online' if friend.get('isOnline', False) else 'Offline'
                            ui.label(status).classes('text-sm text-gray-500')
        except Exception as e:
            logger.error(f'Error refreshing friends list: {str(e)}')
    
    # Main container - use the provided container instead of creating a new one
    with container:
        # Create containers for different sections
        auth_container = ui.column().classes('w-full max-w-md mx-auto')
        chat_container = ui.row().classes('w-full h-[600px] bg-white rounded-lg shadow-lg')
        chat_container.visible = False
        
        # Initialize chat area
        chat_area = ui.column().classes('w-[70%] h-full relative')
        
        # Chat section with split view
        with chat_container:
            # Left side - Friends list (30% width)
            with ui.column().classes('w-[30%] h-full border-r border-gray-200'):
                # Add friend section
                with ui.card().classes('w-full p-2'):
                    ui.label('Add Friend').classes('font-bold mb-2')
                    with ui.row().classes('w-full gap-2'):
                        friend_email = ui.input('Friend Email').classes('flex-grow')
                        
                        def handle_add_friend():
                            try:
                                if not friend_email.value:
                                    ui.notify('Please enter an email address', color='negative')
                                    return
                                
                                firebase_chat.add_friend(
                                    firebase_chat.current_user['localId'],
                                    friend_email.value
                                )
                                friend_email.value = ''
                                refresh_friends_list(friends_list, chat_area)
                                ui.notify('Friend added successfully!', color='positive')
                            except Exception as e:
                                error_message = str(e)
                                if "USER_NOT_FOUND" in error_message:
                                    ui.notify('User not found. Please check the email address.', color='negative')
                                else:
                                    ui.notify(f'Error adding friend: {error_message}', color='negative')
                                logger.error(f'Error adding friend: {error_message}')
                        
                        ui.button('Add', on_click=handle_add_friend).classes('bg-green-500 text-white')
                
                # Friends list
                ui.label('Friends').classes('font-bold p-2')
                friends_list = ui.column().classes('w-full overflow-y-auto')
            
            # Right side - Chat area
            with chat_area:
                show_welcome_message(chat_area)
        
        # Authentication section
        with auth_container:
            with ui.card().classes('w-full p-4'):
                ui.label('Chat Login').classes('text-xl font-bold mb-4 text-center')
                email = ui.input('Email').classes('w-full mb-2')
                password = ui.input('Password', password=True).classes('w-full mb-4')
                error_label = ui.label().classes('text-red-500 text-sm mb-2')
                
                def handle_auth():
                    try:
                        # Sign in or create account
                        user = firebase_chat.sign_in(email.value, password.value)
                        logger.info(f'User signed in: {user}')
                        
                        # Initialize app.storage.user if not exists
                        if not hasattr(app.storage, 'user'):
                            app.storage.user = {}
                            
                        # Update app storage with user info
                        app.storage.user.update({
                            'is_authenticated': True,
                            'uid': user['localId'],
                            'email': email.value
                        })
                        
                        # Hide auth container and show chat container
                        auth_container.visible = False
                        chat_container.visible = True
                        
                        # Set online status and refresh friends list
                        firebase_chat.set_user_status(user['localId'], True)
                        refresh_friends_list(friends_list, chat_area)
                        
                        # Setup cleanup on page unload
                        def cleanup():
                            try:
                                if hasattr(app.storage, 'user'):
                                    firebase_chat.set_user_status(app.storage.user['uid'], False)
                                # Close all message listeners
                                for listener in message_listeners.values():
                                    listener.close()
                            except Exception as e:
                                logger.error(f"Error in cleanup: {str(e)}")
                        
                        app.on_shutdown(cleanup)
                        
                    except Exception as e:
                        error_message = str(e)
                        if "INVALID_LOGIN_CREDENTIALS" in error_message:
                            error_label.set_text('Invalid email or password')
                        elif "EMAIL_EXISTS" in error_message:
                            error_label.set_text('Email already exists')
                        elif "WEAK_PASSWORD" in error_message:
                            error_label.set_text('Password should be at least 6 characters')
                        elif "INVALID_EMAIL" in error_message:
                            error_label.set_text('Invalid email format')
                        else:
                            error_label.set_text(f'Error: {error_message}')
                        logger.error(f'Authentication error: {error_message}')
                
                ui.button('Sign In / Sign Up', on_click=handle_auth).classes('w-full bg-blue-500 text-white') 