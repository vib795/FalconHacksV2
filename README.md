# Password Manager App

This is a simple offline password manager application built using Python and the Tkinter library. The app allows users to securely store, view, update, generate random passwords and delete passwords for various services. Passwords are encrypted using the Fernet symmetric encryption algorithm, and a password history is maintained for each entry. This app is an enhancement on ALL the password manager apps out there because it completely offline and nothing is sent/stored on the cloud. 
### **This app was built because my mom always keeps forgetting her passwords and always needs help resetting them 😊.**

## Prerequisites

- Python 3.x
- Tkinter library
- cryptography library
- sqlite3 library
- pyperclip library

## Installation

1. Clone the repository or download the script.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script
    ```bash
    python password_manager.py
    ```
## Features

- **Add Password:** Store passwords for different services securely.
- **View Passwords:** Display a list of stored passwords with encrypted representations.
- **View Password:** View the decrypted password for a selected service.
- **Delete Password:** Remove a stored password after confirmation.
- **Generate Password:** Create a random password with specified length and complexity.
- **Password History:** View the history of password changes for a selected service.
- **Update Password:** Change the password for a selected service.

## Usage
1. Launch the application.
2. Use the provided buttons to manage passwords.
3. For each stored password, you can view, update, or delete it.
4. Generate strong and random passwords using the "Generate Password" button.

## Security
- Passwords are stored in an encrypted format using the Fernet encryption algorithm.
- Password changes are tracked in a separate history database.

### Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

### License
This project is licensed under the MIT License - see the LICENSE file for details.
```bash
Replace "yourusername" with your actual GitHub username or the organization name where you host the repository.
Feel free to customize this template based on your project's specific details and requirements. Add more sections if needed, such as "Troubleshooting," "Testing," or "Acknowledgments." The goal is to provide clear and comprehensive information for users and potential contributors.

```