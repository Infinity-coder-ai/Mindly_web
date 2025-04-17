import firebase_admin
from firebase_admin import credentials, auth, firestore
import pyrebase
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not FirebaseManager._initialized:
            # Initialize Firebase Admin
            cred = credentials.Certificate("firebase-credentials.json")
            firebase_admin.initialize_app(cred)
            
            # Initialize Pyrebase
            self.firebase_config = {
                "apiKey": os.getenv("FIREBASE_API_KEY"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
                "serviceAccount": "firebase-credentials.json"
            }
            
            self.firebase = pyrebase.initialize_app(self.firebase_config)
            self.auth = self.firebase.auth()
            self.db = firestore.client()
            FirebaseManager._initialized = True

    def sign_up(self, email, password):
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            # Create user document in Firestore
            self.db.collection('users').document(user['localId']).set({
                'email': email,
                'friends': [],
                'created_at': datetime.now()
            })
            return user
        except Exception as e:
            print(f"Error in sign up: {str(e)}")
            return None

    def sign_in(self, email, password):
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            print(f"Error in sign in: {str(e)}")
            return None

    def add_friend(self, user_id, friend_email):
        try:
            # Find friend by email
            friend_query = self.db.collection('users').where('email', '==', friend_email).get()
            if not friend_query:
                return False, "Friend not found"
            
            friend_id = friend_query[0].id
            if friend_id == user_id:
                return False, "Cannot add yourself as friend"
            
            # Add friend to user's friends list
            user_ref = self.db.collection('users').document(user_id)
            user = user_ref.get()
            friends = user.get('friends', [])
            
            if friend_id not in friends:
                friends.append(friend_id)
                user_ref.update({'friends': friends})
                return True, "Friend added successfully"
            return False, "Friend already added"
        except Exception as e:
            print(f"Error adding friend: {str(e)}")
            return False, str(e)

    def get_friends(self, user_id):
        try:
            user = self.db.collection('users').document(user_id).get()
            friends = user.get('friends', [])
            friend_details = []
            
            for friend_id in friends:
                friend = self.db.collection('users').document(friend_id).get()
                if friend.exists:
                    friend_details.append({
                        'id': friend_id,
                        'email': friend.get('email')
                    })
            return friend_details
        except Exception as e:
            print(f"Error getting friends: {str(e)}")
            return []

    def send_message(self, sender_id, receiver_id, message):
        try:
            chat_id = self._get_chat_id(sender_id, receiver_id)
            message_data = {
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'message': message,
                'timestamp': datetime.now()
            }
            
            self.db.collection('chats').document(chat_id).collection('messages').add(message_data)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

    def get_messages(self, user1_id, user2_id):
        try:
            chat_id = self._get_chat_id(user1_id, user2_id)
            messages = self.db.collection('chats').document(chat_id).collection('messages').order_by('timestamp').get()
            return [{'id': msg.id, **msg.to_dict()} for msg in messages]
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []

    def _get_chat_id(self, user1_id, user2_id):
        # Create a consistent chat ID by sorting user IDs
        return '_'.join(sorted([user1_id, user2_id])) 