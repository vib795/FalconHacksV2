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

class PasswordManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("Password Manager")
        # Set the application icon using an ICO file
        icon_path = "icon.ico"  # Replace with the actual path to your ICO file
        master.iconphoto(True, tk.PhotoImage(file=icon_path))

        # Styling
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        # Treeview to display passwords
        self.tree = ttk.Treeview(master, columns=("ID", "Service", "Username", "Password"),
                                 show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Configure column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Service", text="Service")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=4, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Responsive layout
        for i in range(5):
            master.grid_columnconfigure(i, weight=1)
            master.grid_rowconfigure(i, weight=1)

        # Buttons
        tk.Button(master, text="Add Password", command=self.add_password, font=("Helvetica", 12)).grid(row=2, column=0, pady=10, sticky="nsew")
        tk.Button(master, text="View Password", command=self.view_password, font=("Helvetica", 12)).grid(row=2, column=1, pady=10, sticky="nsew")
        tk.Button(master, text="Delete Password", command=self.delete_password_prompt, font=("Helvetica", 12)).grid(row=2, column=2, pady=10, sticky="nsew")

        # Responsive button layout
        for i in range(6):
            master.grid_columnconfigure(i, weight=1)

        # Populate the Treeview initially
        self.view_passwords()

    def view_password(self):
        # Get the selected item from the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a password to view.")
            return

        # Get the ID of the selected password
        password_id = self.tree.item(selected_item, "values")[0]

        # Retrieve the encrypted password from the database
        cursor.execute("SELECT password FROM passwords WHERE id=?", (password_id,))
        encrypted_password = cursor.fetchone()[0]

        # Decrypt the password
        decrypted_password = decrypt_data(encrypted_password)

        # Create a separate window to display the decrypted password
        password_window = tk.Toplevel(self.master)
        password_window.title("Decrypted Password")

        # Text widget to display the decrypted password
        password_display = tk.Text(password_window, height=1, width=30)
        password_display.insert(tk.END, decrypted_password)
        password_display.pack(pady=10)

        # Button to close the window
        tk.Button(password_window, text="Close", command=password_window.destroy, font=("Helvetica", 12)).pack(pady=10)

    def add_password(self):
        service = simpledialog.askstring("Add Password", "Enter service:")
        username = simpledialog.askstring("Add Password", "Enter username:")
        password = simpledialog.askstring("Add Password", "Enter password:")

        if service and username and password:
            save_password(service, username, password)
            messagebox.showinfo("Success", "Password added successfully!")
            # Refresh the view after adding a password
            self.view_passwords()
        else:
            messagebox.showwarning("Warning", "Please fill in all fields.")

    def view_passwords(self):
        # Clear existing items in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get passwords from the database
        passwords = get_passwords()

        # Insert passwords into the Treeview with encrypted passwords
        for password in passwords:
            self.tree.insert("", "end", values=(password[0], password[1], password[2], "Encrypted"))

        # Get the selected item from the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            # messagebox.showinfo(message="Welcome to your personal Password Manager!!")
            return

        # Get the ID of the selected password
        password_id = self.tree.item(selected_item, "values")[0]

        # Retrieve the encrypted password from the database
        cursor.execute("SELECT password FROM passwords WHERE id=?", (password_id,))
        encrypted_password = cursor.fetchone()[0]

        # Decrypt and show the password
        decrypted_password = decrypt_data(encrypted_password)
        messagebox.showinfo("Decrypted Password", f"The decrypted password is:\n{decrypted_password}")
        # Copy to clipboard
        pyperclip.copy(decrypted_password)

    def delete_password_prompt(self):
        # Get the selected item from the Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a password to delete.")
            return

        # Get the ID of the selected password
        password_id = self.tree.item(selected_item, "values")[0]

        # Ask for confirmation
        confirm = messagebox.askyesno("Delete Password", f"Are you sure you want to delete the password with ID {password_id}?")
        if confirm:
            delete_password(password_id)
            messagebox.showinfo("Success", f"Password with ID {password_id} deleted successfully!")
            # Refresh the view after deletion
            self.view_passwords()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()