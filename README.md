# E-Learning Platform Login/Signup

A modern and responsive login/signup system for an e-learning platform built with NiceGUI and MySQL.

## Features

- Modern and responsive UI
- Animated icons
- Beautiful background image
- Secure password hashing
- MySQL database integration
- Form validation
- Smooth transitions between login and signup

## Prerequisites

- Python 3.7+
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your MySQL credentials:
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=elearning_db
```

4. Create the MySQL database:
```sql
CREATE DATABASE elearning_db;
```

## Running the Application

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:8080
```

## Features

- **Login Page**
  - Email and password authentication
  - Form validation
  - Error handling
  - Link to signup page

- **Signup Page**
  - Username, email, and password fields
  - Password confirmation
  - Form validation
  - Link to login page

## Security Features

- Password hashing using bcrypt
- SQL injection prevention
- Input validation
- Secure password storage

## UI Features

- Responsive design
- Modern glassmorphism effect
- Animated icons
- Smooth transitions
- Beautiful background image
- Gradient buttons
- Hover effects 