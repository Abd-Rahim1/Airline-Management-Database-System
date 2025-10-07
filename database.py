import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import bcrypt
from tkinter import messagebox

def connect_to_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Connected to the database")
            return connection
        else:
            print("Failed to connect to the database")
            return None
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Error: {e}")
        return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)