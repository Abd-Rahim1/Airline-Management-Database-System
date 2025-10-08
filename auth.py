import tkinter as tk
from tkinter import messagebox
from mysql.connector import Error
from database import connect_to_database
from admin import admin_dashboard
from passenger import passenger_dashboard, passenger_signup_window

def admin_login_window():
    def admin_login():
        username = admin_username_entry.get()
        password = admin_password_entry.get()

        connection = connect_to_database()  # Ensure this function is implemented correctly
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM User WHERE username=%s AND password=%s", (username, password))
                admin = cursor.fetchone()
                if admin:
                    messagebox.showinfo("Login Success", "Admin logged in successfully!")
                    login_window.destroy()  # Close the login window
                    admin_dashboard()  # Open the admin dashboard
                else:
                    messagebox.showerror("Invalid Credentials", "Username or password is incorrect.")
                    admin_login_window()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            messagebox.showerror("Database Connection Error", "Failed to connect to the database.")

    login_window = tk.Toplevel()
    login_window.title("Admin Login")
    login_window.geometry("400x300")

    tk.Label(login_window, text="Username", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
    tk.Label(login_window, text="Password", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)

    admin_username_entry = tk.Entry(login_window)
    admin_password_entry = tk.Entry(login_window, show="*")

    admin_username_entry.grid(row=0, column=1, pady=10, padx=10)
    admin_password_entry.grid(row=1, column=1, pady=10, padx=10)

    tk.Button(login_window, text="Login", font=("Arial", 14), command=admin_login).grid(row=2, columnspan=2, pady=20)
    login_window.mainloop()

def passenger_login_window():
    def passenger_login():
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        if not name or not email or not password:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            try:
                query = "SELECT * FROM User WHERE email=%s AND password=%s AND role='Passenger'"
                cursor.execute(query, (email, password))
                result = cursor.fetchone()

                if result:
                    messagebox.showinfo("Success", "Login successful!")
                    login_window.destroy()
                    passenger_dashboard()
                else:
                    messagebox.showerror("Error", "Invalid credentials!")
            except Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()

    login_window = tk.Toplevel()
    login_window.title("Passenger Login")
    login_window.geometry("400x300")

    tk.Label(login_window, text="Name", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
    name_entry = tk.Entry(login_window)
    name_entry.grid(row=0, column=1, pady=10, padx=10)

    tk.Label(login_window, text="Email", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)
    email_entry = tk.Entry(login_window)
    email_entry.grid(row=1, column=1, pady=10, padx=10)

    tk.Label(login_window, text="Password", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=2, column=1, pady=10, padx=10)

    tk.Button(login_window, text="Login", font=("Arial", 14), command=passenger_login).grid(row=3, columnspan=2, pady=10)
    tk.Button(login_window, text="Sign Up", font=("Arial", 14), command=passenger_signup_window).grid(row=4, columnspan=2, pady=10)