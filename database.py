import mysql.connector
from mysql.connector import Error
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        try:
            # Print connection details (without password)
            print("\nAttempting to connect to MySQL database:")
            print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
            print(f"User: {os.getenv('DB_USER', 'elearning_user')}")
            print(f"Database: {os.getenv('DB_NAME', 'elearning_db')}")
            
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'elearning_user'),
                password=os.getenv('DB_PASSWORD', 'sql@123'),
                database=os.getenv('DB_NAME', 'elearning_db')
            )
            
            if self.connection.is_connected():
                print("Successfully connected to MySQL database!")
                self.cursor = self.connection.cursor()
                self.create_tables()
        except Error as e:
            print(f"\nDetailed MySQL Connection Error:")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("\nPossible solutions:")
            print("1. Check if MySQL service is running")
            print("2. Verify credentials in .env file")
            print("3. Make sure database exists")
            print("4. Check if user has proper permissions")
            raise

    def create_tables(self):
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(create_users_table)
            self.connection.commit()
            print("Tables created/verified successfully!")
            
            # Check if the table is empty
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.cursor.fetchone()[0]
            print(f"Current number of users in database: {count}")
        except Error as e:
            print(f"Error creating tables: {e}")
            raise

    def register_user(self, username, email, password):
        try:
            # Check if email already exists
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            if self.cursor.fetchone()[0] > 0:
                print(f"Email {email} is already registered")
                return False, "Email already registered"

            # Check if username already exists
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if self.cursor.fetchone()[0] > 0:
                print(f"Username {username} is already taken")
                return False, "Username already taken"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (username, email, hashed_password))
            self.connection.commit()
            print(f"Successfully registered user: {username}")
            return True, "Registration successful"
        except Error as e:
            error_message = str(e)
            print(f"Error registering user: {error_message}")
            return False, f"Registration failed: {error_message}"

    def login_user(self, email, password):
        try:
            # Check if email exists
            self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = self.cursor.fetchone()
            
            if not user:
                print(f"No user found with email: {email}")
                return None, "Email not registered"
            
            if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                print(f"Successful login for user: {user[1]}")
                return {'id': user[0], 'username': user[1], 'email': user[2]}, "Login successful"
            else:
                print(f"Invalid password for user: {user[1]}")
                return None, "Invalid password"
        except Error as e:
            error_message = str(e)
            print(f"Error during login: {error_message}")
            return None, f"Login failed: {error_message}"

    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed.") 