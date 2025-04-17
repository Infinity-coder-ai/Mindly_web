import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase
import logging
import time
from typing import Optional, Dict, List, Any, Callable
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger('FirebaseChat')
logger.setLevel(logging.DEBUG)

class FirebaseChat:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(FirebaseChat, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, config=None):
        if not self.initialized:
            self.config = config or {
                "apiKey": os.getenv("FIREBASE_API_KEY"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                "projectId": os.getenv("FIREBASE_PROJECT_ID"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
                "appId": os.getenv("FIREBASE_APP_ID"),
                "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
                "serviceAccount": "firebase-credentials.json"
            }
            self.current_user = None
            self.id_token = None
            
            # Initialize Firebase Admin SDK
            try:
                # Check if Firebase app is already initialized
                if not firebase_admin._apps:
                    cred = credentials.Certificate("firebase-credentials.json")
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': self.config['databaseURL'],
                        'storageBucket': self.config['storageBucket']
                    })
                    logger.info('Firebase Admin SDK initialized successfully')
                else:
                    logger.info('Firebase Admin SDK already initialized')
            except Exception as e:
                logger.error(f'Error initializing Firebase Admin SDK: {str(e)}')
                raise
            
            # Initialize Pyrebase
            try:
                logger.info(f'Pyrebase configuration: {self.config}')
                self.firebase = pyrebase.initialize_app(self.config)
                self.auth = self.firebase.auth()
                self.db = self.firebase.database()
                logger.info('Pyrebase initialized successfully')
            except Exception as e:
                logger.error(f'Error initializing Pyrebase: {str(e)}')
                raise
            
            self.initialized = True

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user and return their info"""
        logger.info(f'Attempting to sign in user: {email}')
        try:
            # First try to sign in
            try:
                user = self.auth.sign_in_with_email_and_password(email, password)
            except Exception as e:
                # If sign in fails with INVALID_LOGIN_CREDENTIALS, try to create the user
                if "INVALID_LOGIN_CREDENTIALS" in str(e):
                    logger.info(f'User {email} not found, attempting to create new account')
                    # Create new user
                    user = self.auth.create_user_with_email_and_password(email, password)
                    # Sign in the newly created user
                    user = self.auth.sign_in_with_email_and_password(email, password)
                else:
                    raise e

            self.current_user = user
            self.id_token = user['idToken']
            
            # Ensure user data exists in the database
            self._ensure_user_data(user['localId'])
            
            logger.info(f'Successfully signed in user: {email}')
            return user
        except Exception as e:
            logger.error(f'Error signing in: {str(e)}')
            raise

    def _ensure_user_data(self, uid: str):
        """Ensure user data exists in the database"""
        try:
            user_ref = self.db.child('users').child(uid)
            user_data = user_ref.get(token=self.id_token)
            
            if not user_data:
                # Initialize user data if it doesn't exist
                user_ref.set({
                    'friends': {},
                    'status': {
                        'isOnline': True,
                        'lastOnline': time.time()
                    }
                }, token=self.id_token)
                logger.info(f'Created new user data for: {uid}')
        except Exception as e:
            logger.error(f'Error ensuring user data: {str(e)}')
            raise

    def set_user_status(self, uid: str, is_online: bool):
        """Update user's online status"""
        try:
            self.db.child('users').child(uid).child('status').update({
                'isOnline': is_online,
                'lastOnline': time.time()
            }, token=self.id_token)
        except Exception as e:
            logger.error(f'Error updating user status: {str(e)}')
            raise

    def get_friends(self, uid: str) -> List[Dict[str, Any]]:
        """Get user's friends list with their online status"""
        try:
            friends_data = self.db.child('users').child(uid).child('friends').get(token=self.id_token)
            if not friends_data:
                return []
            
            friends = []
            for friend in friends_data.each():
                friend_uid = friend.key()
                friend_data = self.db.child('users').child(friend_uid).get(token=self.id_token)
                if friend_data:
                    friends.append({
                        'uid': friend_uid,
                        'email': friend_data.val().get('email'),
                        'isOnline': friend_data.val().get('status', {}).get('isOnline', False)
                    })
            return friends
        except Exception as e:
            logger.error(f'Error getting friends: {str(e)}')
            raise

    def add_friend(self, uid: str, friend_email: str):
        """Add a friend by email"""
        try:
            # Get friend's UID from email
            friend_user = auth.get_user_by_email(friend_email)
            friend_uid = friend_user.uid
            
            # Add bidirectional friendship
            self.db.child('users').child(uid).child('friends').child(friend_uid).set(True, token=self.id_token)
            self.db.child('users').child(friend_uid).child('friends').child(uid).set(True, token=self.id_token)
            logger.info(f'Successfully added friend: {friend_email}')
        except Exception as e:
            logger.error(f'Error adding friend: {str(e)}')
            raise

    def send_message(self, from_uid: str, to_uid: str, message: str):
        """Send a message to a friend"""
        try:
            message_data = {
                'message': message,
                'timestamp': time.time(),
                'from': from_uid
            }
            
            # Store message in both users' message lists
            self.db.child('users').child(from_uid).child('messages').child(to_uid).push(message_data, token=self.id_token)
            self.db.child('users').child(to_uid).child('messages').child(from_uid).push(message_data, token=self.id_token)
            logger.info(f'Message sent from {from_uid} to {to_uid}')
        except Exception as e:
            logger.error(f'Error sending message: {str(e)}')
            raise

    def listen_to_messages(self, uid: str, friend_uid: str, callback: Callable):
        """Listen to messages between two users"""
        try:
            return self.db.child('users').child(uid).child('messages').child(friend_uid).stream(
                lambda message: callback(message.val()) if message.val() else None,
                token=self.id_token
            )
        except Exception as e:
            logger.error(f'Error setting up message listener: {str(e)}')
            raise

    def set_typing_status(self, uid: str, friend_uid: str, is_typing: bool):
        """Update typing status"""
        try:
            self.db.child('users').child(uid).child('typing').child(friend_uid).set(is_typing, token=self.id_token)
            logger.info(f'Typing status updated for {uid} -> {friend_uid}: {is_typing}')
        except Exception as e:
            logger.error(f'Error updating typing status: {str(e)}')
            raise

    def listen_to_typing(self, friend_uid: str, callback: Callable):
        """Listen to friend's typing status"""
        try:
            return self.db.child('users').child(friend_uid).child('typing').stream(
                lambda typing: callback(typing.val() if typing.val() else False),
                token=self.id_token
            )
        except Exception as e:
            logger.error(f'Error setting up typing listener: {str(e)}')
            raise

# Initialize a global instance
firebase_chat = FirebaseChat()

def get_firebase_chat():
    """Get the global Firebase chat instance"""
    return firebase_chat
