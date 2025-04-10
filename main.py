from nicegui import ui, app
from database import Database
import sys
import atexit
from fastapi import Request
from urllib.parse import unquote
import time
import database as db
import logging
import mysql.connector
from mysql.connector import Error
import re
import os
from dotenv import load_dotenv
import socket

# Configure static files
app.add_static_files('/static', 'static')

# Custom CSS for modern UI
ui.add_head_html('''
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        margin: 0;
        padding: 0;
        min-height: 100vh;
        width: 100%;
    }

    .page-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        min-height: 100vh;
        width: 100%;
        background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    .auth-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 3rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        max-width: 450px;
        width: 90%;
        margin: 5rem auto;
        animation: fadeIn 0.5s ease-out;
        z-index: 1000;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .input-field {
        margin: 1.2rem 0;
        width: 100%;
    }

    .btn-primary {
        background: linear-gradient(45deg, #2196F3, #1976D2);
        border: none;
        padding: 0.9rem 2.5rem;
        border-radius: 25px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        margin: 0.5rem;
        width: 100%;
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
    }

    .icon {
        font-size: 3.5rem;
        margin-bottom: 2rem;
        color: #2196F3;
        animation: float 3s ease-in-out infinite;
        text-align: center;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .link-text {
        color: #2196F3;
        text-decoration: none;
        cursor: pointer;
        text-align: center;
        margin-top: 2rem;
        font-size: 1rem;
        transition: color 0.3s ease;
    }

    .link-text:hover {
        color: #1976D2;
        text-decoration: underline;
    }

    .text-h4 {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }

    .error-message {
        color: #f44336;
        text-align: center;
        margin-top: 1.2rem;
        font-size: 1rem;
    }
</style>
''')

# Root page - always show login first
@ui.page('/')
def index_page():
    # Redirect to login page container
    with ui.column().classes('page-container'):
        with ui.column().classes('auth-container') as login_container:
            from login import show_login
            show_login(login_container)

# Home page route - complete separate page
@ui.page('/home')
def home_page(request: Request):
    """Home page for logged in users"""
    from urllib.parse import unquote
    
    # Import all the section modules
    from dashboard import show_dashboard
    from chatbox import show_chatbox  
    from pdf_listener import show_pdf_listener
    from study_planner import show_planner
    from notes import show_notes
    
    # Add global CSS for animations and page transitions
    ui.add_head_html('''
    <style>
        .nav-button {
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            min-width: 130px;
            text-align: center;
        }
        .nav-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .page-transition {
            animation: slideIn 0.4s ease-out forwards;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        .content-area {
            padding: 24px;
            background-color: #f9fafb;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            min-height: 400px;
            animation: fadeIn 0.6s ease-out forwards;
            margin-top: 20px;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .feature-section {
            margin-top: 32px;
            padding: 20px;
        }
        .header-section {
            position: sticky;
            top: 0;
            z-index: 10;
            background-color: white;
            padding: 10px 0;
            width: 100%;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
    </style>
    ''')
    
    # Extract username and user_id from query parameters
    username = unquote(request.query_params.get('username', 'User'))
    user_id = int(request.query_params.get('user_id', '1'))  # Default to 1 if not provided
    
    # Create the UI layout with proper order
    with ui.column().classes('w-full items-center justify-center'):
        # Header section with welcome message and navigation
        with ui.column().classes('header-section w-full items-center'):
            ui.label(f'Welcome, {username}!').classes('text-2xl font-bold mt-6 mb-4')
            
            # Top navigation buttons in a single row
            with ui.row().classes('w-full justify-center gap-3 mb-6'):
                ui.button('Dashboard', on_click=lambda: switch_section('dashboard')).classes('nav-button bg-indigo-600 text-white')
                ui.button('Chatbox', on_click=lambda: switch_section('chatbox')).classes('nav-button bg-blue-600 text-white')
                ui.button('PDF Listener', on_click=lambda: switch_section('pdf')).classes('nav-button bg-purple-600 text-white')
                ui.button('Study Planner', on_click=lambda: switch_section('planner')).classes('nav-button bg-green-600 text-white')
                ui.button('Take Notes', on_click=lambda: switch_section('notes')).classes('nav-button bg-yellow-600 text-white')
                ui.button('Logout', on_click=lambda: ui.navigate.to('/')).classes('nav-button bg-gray-600 text-white')
        
        # Content container AFTER navigation buttons
        content_container = ui.column().classes('w-3/4 page-transition content-area')
    
    # Function to switch between different sections with animation
    def switch_section(section):
        # Clear the container
        content_container.clear()
        
        # Add the page transition class to trigger animation
        content_container.classes('page-transition')
        
        # Show the selected section content using the imported module functions
        if section == 'dashboard':
            show_dashboard(content_container)
        elif section == 'chatbox':
            show_chatbox(content_container)
        elif section == 'pdf':
            show_pdf_listener(content_container)
        elif section == 'planner':
            show_planner(content_container)
        elif section == 'notes':
            show_notes(content_container, user_id)  # Pass the user_id to show_notes
    
    # Show the default dashboard view on initial load
    show_dashboard(content_container)

# Global database instance
db = None

def main():
    global db
    
    try:
        # Initialize database
        db = Database()
    except Exception as e:
        print(f"\nDatabase Connection Error: {str(e)}")
        print("Please check your MySQL configuration and make sure:")
        print("1. MySQL service is running")
        print("2. Credentials in .env file are correct")
        print("3. Database 'elearning_db' exists")
        db = None

    # Import login module after database is initialized
    from login import set_db
    
    # Set the database instance in the login module
    set_db(db)

    # Shutdown hook to close database connection
    def cleanup():
        global db
        if db and hasattr(db, 'connection') and db.connection.is_connected():
            db.cursor.close()
            db.connection.close()
            print("MySQL connection closed explicitly on shutdown.")

    atexit.register(cleanup)

    # Start the application
    try:
        ports = [8080, 8081, 8082, 8083, 8084]
        for port in ports:
            try:
                ui.run(port=port, title="Mindly - E-Learning Platform", reload=False)
                break
            except OSError:
                if port == ports[-1]:
                    print(f"\nError: Could not start the application on any port.")
                    sys.exit(1)
                continue
    except Exception as e:
        print(f"Error starting the application: {str(e)}")
        cleanup()  # Ensure cleanup on error
        sys.exit(1)

async def handle_login(email: str, password: str):
    """Handle login form submission"""
    print(f"Attempting login with email: {email}")
    
    # Check if we have a database connection
    if not db.check_connection():
        ui.notify('Database connection failed. Please try again later.', color='negative')
        return
    
    # Check for empty fields
    if not email or not password:
        ui.notify('Please fill in all fields', color='warning')
        return
    
    try:
        print("Calling database login function...")
        result, message = db.login_user(email, password)
        
        if result and isinstance(result, dict) and 'username' in result:
            username = result['username']
            user_id = result.get('id', 1)  # Get user_id from result, default to 1 if not found
            print(f"Login successful for user: {username}")
            ui.notify(f'Login successful! Welcome {username}', color='positive')
            # Delay navigation slightly for the notification to be visible
            await ui.sleep(0.8)
            # Navigate to home page with username and user_id as query parameters
            ui.navigate.to(f'/home?username={username}&user_id={user_id}')
        else:
            print(f"Login failed: {message}")
            ui.notify(f'Login failed: {message}', color='negative')
    except Exception as e:
        print(f"Exception during login: {str(e)}")
        ui.notify(f'An error occurred: {str(e)}', color='negative')

def show_dashboard(container):
    """Display the main dashboard interface"""
    with container:
        ui.label('Dashboard').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            ui.label('Welcome to your learning dashboard').classes('text-gray-600')
            
            # Quick access cards
            with ui.row().classes('w-full gap-4'):
                with ui.card().classes('flex-grow p-4 cursor-pointer').on('click', lambda: show_pdf_editor(container)):
                    with ui.column().classes('items-center gap-2'):
                        ui.icon('picture_as_pdf').classes('text-2xl text-red-600')
                        ui.label('PDF Editor').classes('font-semibold')
                        ui.label('Edit and annotate PDFs').classes('text-xs text-gray-600')
                
                with ui.card().classes('flex-grow p-4 cursor-pointer').on('click', lambda: show_planner(container)):
                    with ui.column().classes('items-center gap-2'):
                        ui.icon('calendar_today').classes('text-2xl text-blue-600')
                        ui.label('Study Planner').classes('font-semibold')
                        ui.label('Plan your study schedule').classes('text-xs text-gray-600')
                
                with ui.card().classes('flex-grow p-4 cursor-pointer').on('click', lambda: show_notes(container)):
                    with ui.column().classes('items-center gap-2'):
                        ui.icon('note').classes('text-2xl text-green-600')
                        ui.label('Notes').classes('font-semibold')
                        ui.label('Take and organize notes').classes('text-xs text-gray-600')
            
            # Recent activity
            with ui.card().classes('w-full p-4 mt-4'):
                ui.label('Recent Activity').classes('font-bold mb-2')
                with ui.column().classes('w-full gap-2'):
                    with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 rounded'):
                        ui.icon('picture_as_pdf').classes('text-red-600')
                        ui.label('Uploaded Calculus notes').classes('text-sm')
                        ui.label('2 hours ago').classes('text-xs text-gray-600 ml-auto')
                    
                    with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 rounded'):
                        ui.icon('calendar_today').classes('text-blue-600')
                        ui.label('Added new study session').classes('text-sm')
                        ui.label('5 hours ago').classes('text-xs text-gray-600 ml-auto')
                    
                    with ui.row().classes('w-full items-center p-2 hover:bg-gray-100 rounded'):
                        ui.icon('note').classes('text-green-600')
                        ui.label('Created new note').classes('text-sm')
                        ui.label('Yesterday').classes('text-xs text-gray-600 ml-auto')

if __name__ == "__main__":
    main()