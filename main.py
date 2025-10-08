import tkinter as tk
from auth import admin_login_window, passenger_login_window
from utils import set_background

def main_window():
    global root
    root = tk.Tk()
    root.title("Airline Management System")
    root.attributes("-fullscreen", True)

    set_background(root, "assets/backgrounds/back.jpg")
    set_background(admin_login_window, "assets/backgrounds/admin_dash.jpg")
    set_background(passenger_login_window, "assets/backgrounds/passenger_dash.jpg")

    tk.Label(root, text=" Airline Management System Database", font=("Arial", 46), fg="blue").place(relx=0.5, rely=0.1, anchor="center")

    tk.Button(root, text="Login as Admin", font=("Arial", 20), command=admin_login_window).place(relx=0.5, rely=0.7, anchor="center")
    tk.Button(root, text="Login as Passenger", font=("Arial", 20), command=passenger_login_window).place(relx=0.5, rely=0.8, anchor="center")

    tk.Button(root, text="Exit", font=("Arial", 20), command=root.quit).place(relx=0.5, rely=0.9, anchor="center")

    root.mainloop()

if __name__ == "__main__":
    main_window()