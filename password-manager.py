import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from cryptography.fernet import Fernet
import sqlite3
import secrets
import os
import pyperclip

key_file = "encryption_key.key"

if os.path.exists(key_file):
    with open(key_file, "rb") as key_file:
        key = key_file.read()
else:
    key = Fernet.generate_key()
    with open(key_file, "wb") as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

db_filename = "passwords.db"
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 service TEXT,
                 username TEXT,
                 password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS password_history
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         password_id INTEGER,
                         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         password TEXT)''')

conn.commit()

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()

def save_password(service, username, password):
    encrypted_password = encrypt_data(password)
    cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                   (service, username, encrypted_password))
    conn.commit()

    # Save to history
    password_id = cursor.lastrowid
    cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                           (password_id, encrypted_password))
    conn.commit()

def get_passwords():
    cursor.execute("SELECT * FROM passwords")
    return cursor.fetchall()

def delete_password(password_id):
    # Save to history before deleting
    cursor.execute("SELECT password FROM passwords WHERE id=?", (password_id,))
    encrypted_password = cursor.fetchone()[0]
    cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                           (password_id, encrypted_password))
    conn.commit()

    cursor.execute("DELETE FROM passwords WHERE id=?", (password_id,))
    conn.commit()
