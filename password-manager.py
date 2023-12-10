import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from cryptography.fernet import Fernet
import sqlite3
import secrets
import os
import pyperclip
import logging as logger

try:
    key_file = "encryption_key.key"

    if os.path.exists(key_file):
        with open(key_file, "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as key_file:
            key_file.write(key)

    cipher_suite = Fernet(key)
except Exception as e:
    logger.error(f"Error occurred in loading the encryption key fpr the app.")
    raise Exception

try:
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
except Exception as e:
    logger.error(f"An error occurred while creating tables in the DB. {str(e)}")
    raise Exception


def encrypt_data(data):
    try:
        return cipher_suite.encrypt(data.encode())
    except Exception as e:
        logger.error(f"An error occurred in encrypting your password. {str(e)}")
        raise Exception
    
def decrypt_data(data):
    try:
        return cipher_suite.decrypt(data).decode()
    except Exception as e:
        logger.error(f"An error occurred while decrypting your password. {str(e)}")
        raise Exception

def save_password(service, username, password):
    try:
        encrypted_password = encrypt_data(password)
        cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                    (service, username, encrypted_password))
        conn.commit()
    except Exception as e:
        logger.error(f"An error occurred in inserting password to the current password table. {str(e)}")
        raise Exception
    try:
        # Save to history
        password_id = cursor.lastrowid
        cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                            (password_id, encrypted_password))
        conn.commit()
    except Exception as e:
        logger.error(f"An error occurred in inserting password to the history password table. {str(e)}")
        raise Exception

def get_passwords():
    try:
        cursor.execute("SELECT * FROM passwords")
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"An error occurred in fetching and loading the main view with all the entries. {str(e)}")

def delete_password(password_id):
    try:
        # Save to history before deleting
        cursor.execute("SELECT password FROM passwords WHERE id=?", (password_id,))
        encrypted_password = cursor.fetchone()[0]
        cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                            (password_id, encrypted_password))
        conn.commit()
    except Exception as e:
        logger.error(f"An error occurred during password delete for {password_id}. Error occurred in updating history of the {password_id}. {str(e)}")
    try:
        cursor.execute("DELETE FROM passwords WHERE id=?", (password_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"An error occurred in deleting password from the DB. {str(e)}")

class PasswordManagerApp:
    def __init__(self, master):
        try:
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
            tk.Button(master, text="Generate Password", command=self.generate_password, font=("Helvetica", 12)).grid(row=2, column=4, pady=10, sticky="nsew")
            tk.Button(master, text="Password History", command=self.show_password_history, font=("Helvetica", 12)).grid(row=2, column=5, pady=10, sticky="nsew")
            tk.Button(master, text="Update Password", command=self.update_password, font=("Helvetica", 12)).grid(row=2, column=3, pady=10, sticky="nsew")

            # Responsive button layout
            for i in range(6):
                master.grid_columnconfigure(i, weight=1)

            # Populate the Treeview initially
            self.view_passwords()
        except Exception as e:
            logger.error(f"Error in __init__. Error loading app. {str(e)}")
            raise Exception

    def view_password(self):
        try:
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
        except Exception as e:
            logger.error(f"An error occurred in the view_password method. {str(e)}")
            raise Exception

    def add_password(self):
        try:
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
        except Exception as e:
            logger.error(f"An error occurred in the add_password method. {str(e)}")
            raise Exception

    def view_passwords(self):
        try:
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
        except Exception as e:
            logger.error(f"An error occurred in the view_passwords method. {str(e)}")
            raise Exception

    def delete_password_prompt(self):
        try:
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
        except Exception as e:
            logger.error(f"An error occurred in the delete_password_prompt method. {str(e)}")
            raise Exception

    def generate_password(self):
        try:
            length = simpledialog.askinteger("Password Generator", "Enter password length:")
            if length:
                complexity = simpledialog.askstring("Password Generator", "Enter password complexity (low, medium, high):")
                if complexity in ['low', 'medium', 'high']:
                    password = self.generate_random_password(length, complexity)
                    
                    # Display the generated password in a separate window
                    generated_password_window = tk.Toplevel(self.master)
                    generated_password_window.title("Generated Password")

                    # Text widget to display the generated password
                    password_display = tk.Text(generated_password_window, height=1, width=30)
                    password_display.insert(tk.END, password)
                    password_display.pack(pady=10)

                    # Button to close the window
                    tk.Button(generated_password_window, text="Close", command=generated_password_window.destroy, font=("Helvetica", 12)).pack(pady=10)
                else:
                    messagebox.showwarning("Warning", "Invalid complexity level. Please choose low, medium, or high.")
        except Exception as e:
            logger.error(f"An error occurred in the generate_password method. {str(e)}")
            raise Exception

    def generate_random_password(self, length, complexity):
        try:
            chars_low = "abcdefghijklmnopqrstuvwxyz"
            chars_medium = chars_low + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            chars_high = chars_medium + "0123456789!@#$%^&*()_-+=<>?/"

            if complexity == 'low':
                chars = chars_low
            elif complexity == 'medium':
                chars = chars_medium
            else:
                chars = chars_high

            password = ''.join(secrets.choice(chars) for _ in range(length))
            return password
        except Exception as e:
            logger.error(f"An error occurred in the generate_random_password method. {str(e)}")
            raise Exception

    def update_password(self):
        try:
            # Get the selected item from the Treeview
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a password to update.")
                return

            # Get the ID of the selected password
            password_id = self.tree.item(selected_item, "values")[0]

            # Get the current encrypted password from the database
            cursor.execute("SELECT password FROM passwords WHERE id=?", (password_id,))
            current_encrypted_password = cursor.fetchone()[0]

            # Ask the user for the new password
            new_password = simpledialog.askstring("Update Password", "Enter the new password:")
            if new_password:
                # Encrypt and update the password in the database
                new_encrypted_password = encrypt_data(new_password)
                cursor.execute("UPDATE passwords SET password=? WHERE id=?", (new_encrypted_password, password_id))
                conn.commit()

                # Save the previous and new password to history
                # history_cursor.
                cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                                    (password_id, current_encrypted_password))
                # history_cursor.
                cursor.execute("INSERT INTO password_history (password_id, password) VALUES (?, ?)",
                                    (password_id, new_encrypted_password))
                # history_conn.
                conn.commit()

                messagebox.showinfo("Success", "Password updated successfully!")
                # Refresh the view after updating the password
                self.view_passwords()
        except Exception as e:
            logger.error(f"An error occurred in the update_password method. {str(e)}")
            raise Exception

    def show_password_history(self):
        try:
            # Fetch password history from the database
            password_id = self.get_selected_password_id()
            if password_id is not None:
                # history_cursor.
                cursor.execute("SELECT timestamp, password FROM password_history WHERE password_id=? ORDER BY timestamp DESC",
                                    (password_id,))
                history = cursor.fetchall() #history_cursor.fetchall()

                # Display history in a new window
                history_window = tk.Toplevel(self.master)
                history_window.title("Password History")

                # Treeview to display history
                tree = ttk.Treeview(history_window, columns=("Timestamp", "Password"),
                                    show="headings", selectmode="browse")
                tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

                # Configure column headings
                tree.heading("Timestamp", text="Timestamp")
                tree.heading("Password", text="Password")

                # Add vertical scrollbar
                scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
                scrollbar.grid(row=1, column=1, sticky="ns")
                tree.configure(yscrollcommand=scrollbar.set)

                # Responsive layout
                history_window.grid_columnconfigure(0, weight=1)
                history_window.grid_rowconfigure(1, weight=1)

                # Populate the Treeview with history
                for entry in history:
                    decrypted_password = decrypt_data(entry[1])
                    tree.insert("", "end", values=(entry[0], decrypted_password))
        except Exception as e:
            logger.error(f"An error occurred in show_password_history method. {str(e)}")
            raise Exception

    def get_selected_password_id(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a password.")
                return None

            # Get the ID of the selected password
            return self.tree.item(selected_item, "values")[0]
        except Exception as e:
            logger.error(f"An error occurred in the get_selected_password_id method. {str(e)}")
            raise Exception


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()