from nicegui import ui
from database import Database
import bcrypt

# Global database instance (will be set by main.py)
db = None

def set_db(database_instance):
    """Set the database instance from main.py"""
    global db
    db = database_instance

def show_login(login_container):
    """Display the login form"""
    print("Displaying login form")  # Debugging output
    login_container.clear()
    
    # Ensure the container has the correct class for styling
    login_container.classes('auth-container')
    
    # Add global CSS for the login page
    ui.add_head_html('''
    <style>
        .auth-card {
            max-width: 420px;
            width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            padding: 32px;
            transition: all 0.3s ease;
        }
        .auth-card:hover {
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        .auth-container {
            min-height: 100vh;
            background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .page-container {
            width: 100%;
            min-height: 100vh;
        }
        .logo-container {
            margin-bottom: 24px;
            text-align: center;
        }
        .logo-icon {
            font-size: 48px;
            color: #4F46E5;
        }
        .brand-name {
            font-size: 28px;
            font-weight: 700;
            color: #1F2937;
            margin-top: 8px;
        }
        .form-title {
            font-size: 24px;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 24px;
            text-align: center;
        }
        .input-container {
            margin-bottom: 20px;
            width: 100%;
        }
        .input-field {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
            padding: 10px;
        }
        .input-field:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        .btn-primary {
            background-color: #4F46E5;
            color: white;
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px;
            margin-top: 24px;
            transition: all 0.2s ease;
        }
        .btn-primary:hover {
            background-color: #4338CA;
            transform: translateY(-2px);
        }
        .link-container {
            display: flex;
            justify-content: center;
            margin-top: 24px;
        }
        .link-text {
            color: #6B7280;
            font-size: 14px;
        }
        .signup-btn {
            color: #4F46E5;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-left: 5px;
        }
        .signup-btn:hover {
            text-decoration: underline;
        }
        .footer-text {
            text-align: center;
            margin-top: 24px;
            font-size: 12px;
            color: #6B7280;
        }
    </style>
    ''')
    
    # Create a card for the login form
    with login_container:
        with ui.card().classes('auth-card'):
            # Logo and brand
            with ui.column().classes('logo-container'):
                ui.icon('school').classes('logo-icon')
                ui.label('Mindly').classes('brand-name')
                ui.label('Login to Your Account').classes('form-title')
            
            # Login Form
            with ui.column().classes('input-container'):
                email_input = ui.input('Email').props('outlined').classes('input-field')
            
            with ui.column().classes('input-container'):
                password_input = ui.input('Password', password=True).props('outlined').classes('input-field')
                
            with ui.row().classes('justify-between items-center w-full'):
                ui.checkbox('Remember me').classes('text-sm')
                ui.button('Forgot Password?', on_click=lambda: show_forgot_password()).props('flat').classes('text-sm text-indigo-600')
            
            ui.button('Login', on_click=lambda: handle_login(email_input.value, password_input.value, login_container)).classes('btn-primary')
            
            # Sign up link
            with ui.row().classes('link-container'):
                ui.label("Don't have an account?").classes('link-text')
                ui.button('Sign up', on_click=lambda: show_signup(login_container)).classes('signup-btn').props('flat')
            
            # Footer
            ui.label('© 2023 Mindly Learning Platform. All rights reserved.').classes('footer-text')

def show_forgot_password():
    """Display the forgot password form"""
    with ui.dialog() as dialog, ui.card().classes('auth-card'):
        ui.icon('school').classes('logo-icon')
        ui.label('Mindly').classes('brand-name')
        ui.label('Reset Your Password').classes('form-title')
        
        email_input = ui.input('Email').props('outlined').classes('input-field')
        new_password = ui.input('New Password', password=True).props('outlined').classes('input-field')
        confirm_password = ui.input('Confirm Password', password=True).props('outlined').classes('input-field')
        ui.label('Enter your email and new password').classes('text-sm text-gray-600 mt-2')
        
        with ui.row().classes('justify-between w-full'):
            ui.button('Update Password', on_click=lambda: handle_reset_password(
                email_input.value, 
                new_password.value, 
                confirm_password.value, 
                dialog
            )).classes('btn-primary')
            ui.button('Cancel', on_click=dialog.close).props('flat')
    
    dialog.open()

def handle_reset_password(email, new_password, confirm_password, dialog):
    """Handle password reset"""
    global db
    
    if not db:
        ui.notify('Database connection is not available', color='negative')
        return
    
    if not email or not new_password or not confirm_password:
        ui.notify('Please fill in all fields', color='warning')
        return
    
    if new_password != confirm_password:
        ui.notify('Passwords do not match', color='negative')
        return
    
    try:
        # Check if email exists
        cursor = db.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            ui.notify('No account found with this email', color='negative')
            return
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update the password in the database
        cursor = db.connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Password updated successfully! Please login with your new password.', color='positive')
        dialog.close()
        
    except Exception as e:
        ui.notify(f'Error updating password: {str(e)}', color='negative')

def show_signup(login_container):
    """Display the signup form"""
    print("Displaying signup form")  # Debugging output
    login_container.clear()
    
    # Set the container class for styling
    login_container.classes('auth-container')
    
    # Create a function to handle login button click
    def go_to_login():
        print("Going back to login form")
        login_container.clear()
        show_login(login_container)
    
    # Add global CSS for the signup page
    ui.add_head_html('''
    <style>
        .auth-card {
            max-width: 420px;
            width: 100%;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            padding: 32px;
            transition: all 0.3s ease;
        }
        .auth-card:hover {
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        .auth-container {
            min-height: 100vh;
            background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
            padding: 40px 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .page-container {
            width: 100%;
            min-height: 100vh;
        }
        .logo-container {
            margin-bottom: 24px;
            text-align: center;
        }
        .logo-icon {
            font-size: 48px;
            color: #4F46E5;
        }
        .brand-name {
            font-size: 28px;
            font-weight: 700;
            color: #1F2937;
            margin-top: 8px;
        }
        .form-title {
            font-size: 24px;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 24px;
            text-align: center;
        }
        .input-container {
            margin-bottom: 20px;
            width: 100%;
        }
        .input-field {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
            padding: 10px;
        }
        .input-field:focus {
            border-color: #4F46E5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        .btn-primary {
            background-color: #4F46E5;
            color: white;
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px;
            margin-top: 24px;
            transition: all 0.2s ease;
        }
        .btn-primary:hover {
            background-color: #4338CA;
            transform: translateY(-2px);
        }
        .link-container {
            display: flex;
            justify-content: center;
            margin-top: 24px;
        }
        .link-text {
            color: #6B7280;
            font-size: 14px;
        }
        .signup-btn {
            color: #4F46E5;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-left: 5px;
        }
        .signup-btn:hover {
            text-decoration: underline;
        }
        .footer-text {
            text-align: center;
            margin-top: 24px;
            font-size: 12px;
            color: #6B7280;
        }
    </style>
    ''')
    
    # Create a card for the signup form
    with login_container:
        with ui.card().classes('auth-card'):
            # Logo and brand
            with ui.column().classes('logo-container'):
                ui.icon('school').classes('logo-icon')
                ui.label('Mindly').classes('brand-name')
                ui.label('Create Your Account').classes('form-title')
            
            # Signup Form
            with ui.column().classes('input-container'):
                username_input = ui.input('Username').props('outlined').classes('input-field')
                
            with ui.column().classes('input-container'):
                email_input = ui.input('Email').props('outlined').classes('input-field')
                
            with ui.column().classes('input-container'):
                password_input = ui.input('Password', password=True).props('outlined').classes('input-field')
                
            with ui.column().classes('input-container'):
                confirm_password_input = ui.input('Confirm Password', password=True).props('outlined').classes('input-field')
            
            ui.button('Sign Up', on_click=lambda: handle_signup(
                username_input.value, 
                email_input.value, 
                password_input.value, 
                confirm_password_input.value,
                login_container
            )).classes('btn-primary')
            
            # Sign up link
            with ui.row().classes('link-container'):
                ui.label('Already have an account?').classes('link-text')
                ui.button('Login', on_click=go_to_login).classes('signup-btn').props('flat')
            
            # Terms and conditions
            ui.label('By signing up, you agree to our Terms of Service and Privacy Policy').classes('footer-text')

def handle_login(email, password, login_container):
    """Handle login form submission"""
    global db
    
    if not db:
        ui.notify('Database connection is not available', color='negative')
        return

    print(f"\nAttempting login for email: {email}")
    
    if not email or not password:
        print("Error: Missing email or password")
        ui.notify('Please fill in all fields', color='warning')
        return
    
    try:
        print("Calling database login_user function...")
        result, message = db.login_user(email, password)
        if result:
            print(f"Login successful for user: {result['username']}")
            ui.notify(f"Welcome back, {result['username']}!", color='positive')
            
            # Use ui.navigate.to() for page transition with properly formatted URL
            username = result['username']
            ui.timer(0.8, lambda: ui.navigate.to(f'/home?username={username}'))
        else:
            print(f"Login failed: {message}")
            ui.notify(message, color='negative')
    except Exception as e:
        print(f"Exception during login: {str(e)}")
        ui.notify(f'Login error: {str(e)}', color='negative')

def handle_signup(username, email, password, confirm_password, login_container):
    """Handle signup form submission"""
    global db
    
    if not db:
        ui.notify('Database connection is not available', color='negative')
        return
    
    print(f"\nAttempting to register user: {username}, email: {email}")
    
    # Validate inputs
    if not username or not email or not password or not confirm_password:
        print("Error: Missing required fields")
        ui.notify('Please fill in all fields', color='warning')
        return
    
    if password != confirm_password:
        print("Error: Passwords do not match")
        ui.notify('Passwords do not match', color='negative')
        return
    
    try:
        success, message = db.register_user(username, email, password)
        if success:
            print(f"User registered successfully: {username}")
            ui.notify('Registration successful! Please login.', color='positive')
            # Clear the container and show login form
            login_container.clear()
            show_login(login_container)
        else:
            print(f"Registration failed: {message}")
            ui.notify(message, color='negative')
    except Exception as e:
        print(f"Exception during registration: {str(e)}")
        ui.notify(f'Registration error: {str(e)}', color='negative') 