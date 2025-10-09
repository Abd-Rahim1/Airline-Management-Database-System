from database import connect_to_database
from utils import (
    fetch_airplanes, 
    fetch_pilots, 
    fetch_airports, 
    fetch_flights, 
    fetch_roles,
)
# May also need:
from tkcalendar import DateEntry
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from utils import set_background
import re
from PIL import Image, ImageTk

def admin_dashboard():
    # Create the admin dashboard window
    admin_window = tk.Toplevel()  # Use Toplevel instead of Tk
    admin_window.title("Admin Dashboard")

    # Set the window to full screen
    admin_window.attributes("-fullscreen", True)

    # Set the background using Canvas
    try:
        # Load the background image
        set_background(admin_window, "assets/backgrounds/admin_dash.jpg")
        img = img.resize((admin_window.winfo_screenwidth(), admin_window.winfo_screenheight()), Image.Resampling.LANCZOS)
        bg_img = ImageTk.PhotoImage(img)

        # Create a Canvas and set the image as background
        canvas = tk.Canvas(admin_window, width=admin_window.winfo_screenwidth(), height=admin_window.winfo_screenheight())
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_img, anchor="nw")

        # Keep the background image in memory by attaching it to the window
        admin_window.bg_img = bg_img

    except Exception as e:
        print(f"Error loading background image: {e}")
        admin_window.configure(bg="white")  # Fallback to white background

    # Add buttons for admin actions
    tk.Button(admin_window, text="Manage Airs", font=("Arial", 20), command=lambda: aircraft_and_airline_window()).place(relx=0.05, rely=0.15, anchor="w")
    tk.Button(admin_window, text="Manage Flights", font=("Arial", 20), command=lambda: manage_flights(admin_window)).place(relx=0.05, rely=0.25, anchor="w")
    tk.Button(admin_window, text="Manage Crew Members", font=("Arial", 20), command=lambda: open_crew_management_window()).place(relx=0.05, rely=0.35, anchor="w")
    tk.Button(admin_window, text="Manage Passengers", font=("Arial", 20), command=lambda: manage_passenger(admin_window)).place(relx=0.05, rely=0.45, anchor="w")
    tk.Button(admin_window, text="View Bookings", font=("Arial", 20), command=lambda: view_bookings()).place(relx=0.05, rely=0.55, anchor="w")
    tk.Button(admin_window, text="Exit", font=("Arial", 20), command=admin_window.destroy).place(relx=0.05, rely=0.9, anchor="w")

def aircraft_and_airline_window():
    # Create a new top-level window
    management_window = tk.Toplevel()
    management_window.title("Aircraft and Airline Management")  # Updated title
    management_window.geometry("1450x800+25+25")
    
    # Add a label to the window
    tk.Label(management_window, text="Aircraft and Airline Management", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")
    
    # Create buttons for managing different entities
    tk.Button(management_window, text="Manage Airline", font=("Arial", 20), command=lambda: manage_airline(management_window)).place(relx=0.05, rely=0.15, anchor="w")
    tk.Button(management_window, text="Manage Airplane", font=("Arial", 20), command=lambda: manage_airplane(management_window)).place(relx=0.05, rely=0.25, anchor="w")
    tk.Button(management_window, text="Manage Airports", font=("Arial", 20), command=lambda: manage_airport(management_window)).place(relx=0.05, rely=0.35, anchor="w")
    tk.Button(management_window, text="Exit", font=("Arial", 20), command=management_window.destroy).place(relx=0.05, rely=0.85, anchor="w")

def manage_airplane(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Airplanes")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage airplanes window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    airplane_model = tk.StringVar()
    airplane_registration = tk.StringVar()
    airplane_capacity = tk.StringVar()

    # Table for displaying airplanes
    def load_airplanes():
        # Clear the table before loading new data
        for item in airplane_table.get_children():
            airplane_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Airplane")  # Load all airplanes
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    airplane_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading airplanes: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Insert Airplane
    def insert_airplane():
        conn = None
        try:
            # Validate fields
            if not airplane_model.get().strip() or not airplane_registration.get().strip() or not airplane_capacity.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Airplane 
                    (model, registration, capacity)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (
                    airplane_model.get().strip(), airplane_registration.get().strip(), airplane_capacity.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Airplane added successfully!")
                load_airplanes()  # Reload the table
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting airplane: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Update Airplane
    def update_airplane():
        selected_item = airplane_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No airplane selected.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        airplane_data = airplane_table.item(selected_item[0], "values")
        airplane_id_to_update = airplane_data[0]  # Assuming the first column is Airplane ID

        updates = []
        params = []

        if airplane_model.get():
            updates.append("model = %s")
            params.append(airplane_model.get().strip())
        if airplane_registration.get():
            updates.append("registration = %s")
            params.append(airplane_registration.get().strip())
        if airplane_capacity.get():
            updates.append("capacity = %s")
            params.append(airplane_capacity.get().strip())

        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        params.append(airplane_id_to_update)

        update_query = f"UPDATE Airplane SET {', '.join(updates)} WHERE airplane_id = %s"

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            messagebox.showinfo("Success", f"Airplane ID {airplane_id_to_update} updated successfully!")
            load_airplanes()
            admin_dashboard()
            aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating airplane: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Delete Airplane
    def delete_airplane():
        selected_item = airplane_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an airplane to delete")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        airplane_id = airplane_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Airplane ID {airplane_id}?")
        if not confirm:
            admin_dashboard()
            aircraft_and_airline_window()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Airplane WHERE airplane_id = %s", (airplane_id,))
                conn.commit()

                messagebox.showinfo("Success", "Airplane deleted successfully!")
                load_airplanes()
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting airplane: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Airplanes", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Model:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airplane_model).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Registration:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airplane_registration).grid(row=2, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Capacity:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airplane_capacity).grid(row=3, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Airplane Information:", font=("Arial", 18, "bold"), bg="white").grid(row=4, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all airplanes
    airplane_table = ttk.Treeview(manage_frame, columns=("airplane_id", "model", "registration", "capacity"), show="headings")
    
    # Define column headings
    airplane_table.heading("airplane_id", text="Airplane ID")
    airplane_table.heading("model", text="Model")
    airplane_table.heading("registration", text="Registration")
    airplane_table.heading("capacity", text="Capacity")

    # Set column widths
    airplane_table.column("airplane_id", width=100)
    airplane_table.column("model", width=200)
    airplane_table.column("registration", width=200)
    airplane_table.column("capacity", width=100)

    # Add scrollbar
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=airplane_table.yview)
    airplane_table.configure(yscrollcommand=scrollbar.set)
    airplane_table.grid(row=5, column=0, columnspan=8, pady=10, padx=5)
    scrollbar.grid(row=5, column=8, sticky="ns", padx=(0, 5))

    # Buttons below the table
    add_button = tk.Button(manage_frame, text="Add Airplane", bg="#4CAF50", fg="white", command=insert_airplane)
    add_button.grid(row=6, column=0, padx=5, pady=10)

    update_button = tk.Button(manage_frame, text="Update Airplane", bg="#2196F3", fg="white", command=update_airplane)
    update_button.grid(row=6, column=1, padx=5, pady=10)

    delete_button = tk.Button(manage_frame, text="Delete Airplane", bg="#f44336", fg="white", command=delete_airplane)
    delete_button.grid(row=6, column=2, padx=5, pady=10)

    # Load the airplane data into the table
    load_airplanes()

def manage_airline(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Airlines")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage airlines window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    airline_name = tk.StringVar()
    airline_code = tk.StringVar()

    # Table for displaying airlines
    def load_airlines():
        # Clear the table before loading new data
        for item in airline_table.get_children():
            airline_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Airline")  # Load all airlines
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    airline_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading airlines: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Insert Airline
    def insert_airline():
        conn = None
        try:
            # Validate fields
            if not airline_name.get().strip() or not airline_code.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Airline 
                    (name, code)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (
                    airline_name.get().strip(), airline_code.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Airline added successfully!")
                load_airlines()  # Reload the table
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting airline: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Update Airline
    def update_airline():
        selected_item = airline_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No airline selected.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        airline_data = airline_table.item(selected_item[0], "values")
        airline_id_to_update = airline_data[0]  # Assuming the first column is Airline ID

        updates = []
        params = []

        if airline_name.get():
            updates.append("name = %s")
            params.append(airline_name.get().strip())
        if airline_code.get():
            updates.append("code = %s")
            params.append(airline_code.get().strip())

        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        params.append(airline_id_to_update)

        update_query = f"UPDATE Airline SET {', '.join(updates)} WHERE airline_id = %s"

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            messagebox.showinfo("Success", f"Airline ID {airline_id_to_update} updated successfully!")
            load_airlines()
            admin_dashboard()
            aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating airline: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Delete Airline
    def delete_airline():
        selected_item = airline_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an airline to delete")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        airline_id = airline_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Airline ID {airline_id}?")
        if not confirm:
            admin_dashboard()
            aircraft_and_airline_window()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Airline WHERE airline_id = %s", (airline_id,))
                conn.commit()

                messagebox.showinfo("Success", "Airline deleted successfully!")
                load_airlines()
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting airline: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Airlines", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airline_name).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Code:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airline_code).grid(row=2, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Airline Information:", font=("Arial", 18, "bold"), bg="white").grid(row=4, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all airlines
    airline_table = ttk.Treeview(manage_frame, columns=("airline_id", "name", "code"), show="headings")
    
    # Define column headings
    airline_table.heading("airline_id", text="Airline ID")
    airline_table.heading("name", text="Name")
    airline_table.heading("code", text="Code")

    # Set column widths
    airline_table.column("airline_id", width=100)
    airline_table.column("name", width=200)
    airline_table.column("code", width=200)

    # Add scrollbar
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=airline_table.yview)
    airline_table.configure(yscrollcommand=scrollbar.set)
    airline_table.grid(row=5, column=0, columnspan=8, pady=10, padx=5)
    scrollbar.grid(row=5, column=8, sticky="ns", padx=(0, 5))

    # Buttons below the table
    add_button = tk.Button(manage_frame, text="Add Airline", bg="#4CAF50", fg="white", command=insert_airline)
    add_button.grid(row=6, column=0, padx=5, pady=10)

    update_button = tk.Button(manage_frame, text="Update Airline", bg="#2196F3", fg="white", command=update_airline)
    update_button.grid(row=6, column=1, padx=5, pady=10)

    delete_button = tk.Button(manage_frame, text="Delete Airline", bg="#f44336", fg="white", command=delete_airline)
    delete_button.grid(row=6, column=2, padx=5, pady=10)

    # Load the airline data into the table
    load_airlines()

def manage_airport(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Airports")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage airports window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    airport_name = tk.StringVar()
    airport_location = tk.StringVar()
    airport_capacity = tk.StringVar()

    # Table for displaying airports
    def load_airports():
        # Clear the table before loading new data
        for item in airport_table.get_children():
            airport_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Airport")  # Load all airports
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    airport_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading airports: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Insert Airport
    def insert_airport():
        conn = None
        try:
            # Validate and parse fields
            if not airport_name.get().strip() or not airport_location.get().strip() or not airport_capacity.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Airport 
                    (name, location, capacity)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (
                    airport_name.get().strip(), airport_location.get().strip(), airport_capacity.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Airport added successfully!")
                load_airports()  # Reload the table
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting airport: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Update Airport
    def update_airport():
        # Check if an airport is selected in the table
        selected_item = airport_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No airport selected.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        airport_data = airport_table.item(selected_item[0], "values")
        airport_id_to_update = airport_data[0]  # Assuming the first column is Airport ID

        # Prepare updated data
        updates = []
        params = []

        if airport_name.get():
            updates.append("name = %s")
            params.append(airport_name.get().strip())
        if airport_location.get():
            updates.append("location = %s")
            params.append(airport_location.get().strip())
        if airport_capacity.get():
            updates.append("capacity = %s")
            params.append(airport_capacity.get().strip())

        # Ensure at least one field is being updated
        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            aircraft_and_airline_window()
            return

        # Add the airport ID to the parameters
        params.append(airport_id_to_update)

        # Create the dynamic SQL query
        update_query = f"UPDATE Airport SET {', '.join(updates)} WHERE airport_id = %s"

        try:
            # Connect to the database and execute the query
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            # Show success message and reload the table
            messagebox.showinfo("Success", f"Airport ID {airport_id_to_update} updated successfully!")
            admin_dashboard()
            load_airports()
            aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating airport: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Delete Airport
    def delete_airport():
        selected_item = airport_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an airport to delete")
            return

        airport_id = airport_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Airport ID {airport_id}?")
        if not confirm:
            admin_dashboard()
            aircraft_and_airline_window()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Airport WHERE airport_id = %s", (airport_id,))
                conn.commit()

                messagebox.showinfo("Success", "Airport deleted successfully!")
                load_airports()
                admin_dashboard()
                aircraft_and_airline_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting airport: {str(e)}")
            admin_dashboard()
            aircraft_and_airline_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Airports", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airport_name).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Location:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airport_location).grid(row=2, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Capacity:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=airport_capacity).grid(row=3, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Airport Information:", font=("Arial", 18, "bold"), bg="white").grid(row=4, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all airports
    airport_table = ttk.Treeview(manage_frame, columns=("airport_id", "name", "location", "capacity"), show="headings")
    
    # Define column headings
    airport_table.heading("airport_id", text="Airport ID")
    airport_table.heading("name", text="Name")
    airport_table.heading("location", text="Location")
    airport_table.heading("capacity", text="Capacity")

    # Set column widths
    airport_table.column("airport_id", width=100)
    airport_table.column("name", width=200)
    airport_table.column("location", width=300)
    airport_table.column("capacity", width=100)

    # Add scrollbar
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=airport_table.yview)
    airport_table.configure(yscrollcommand=scrollbar.set)
    airport_table.grid(row=5, column=0, columnspan=8, pady=10, padx=5)
    scrollbar.grid(row=5, column=8, sticky="ns", padx=(0, 5))

    # Buttons below the table
    add_button = tk.Button(manage_frame, text="Add Airport", bg="#4CAF50", fg="white", command=insert_airport)
    add_button.grid(row=6, column=0, padx=5, pady=10)

    update_button = tk.Button(manage_frame, text="Update Airport", bg="#2196F3", fg="white", command=update_airport)
    update_button.grid(row=6, column=1, padx=5, pady=10)

    delete_button = tk.Button(manage_frame, text="Delete Airport", bg="#f44336", fg="white", command=delete_airport)
    delete_button.grid(row=6, column=2, padx=5, pady=10)

    # Load the airport data into the table
    load_airports()

def manage_flights(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Flights")
    manage_window.geometry("1500x800")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage flights window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Fetch data for OptionMenus
    airplanes = fetch_airplanes()
    pilots = fetch_pilots()
    airports = fetch_airports()

    # Entry Widgets
    departure_date = tk.StringVar()
    departure_time = tk.StringVar()
    arrival_date = tk.StringVar()
    arrival_time = tk.StringVar()
    status = tk.StringVar()
    total_seats = tk.StringVar()
    economy_price = tk.StringVar()
    business_price = tk.StringVar()
    price_last_updated = tk.StringVar()
    selected_pilot = tk.StringVar()
    selected_departure_airport = tk.StringVar()
    selected_arrival_airport = tk.StringVar()
    selected_airplane = tk.StringVar()

    # Table for displaying flights
    def load_flights():
        # Clear the table before loading new data
        for item in flight_table.get_children():
            flight_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Flight")
                rows = cursor.fetchall()
                
                # Debug: Print the rows to check if the total_seats is updated in the database
                #print("Loaded flights data:", rows)

                # Insert rows into the table
                for row in rows:
                    # Debug: Check if row is correctly formatted
                    #print("Inserting row:", row)
                    flight_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading flights: {str(e)}")
        finally:
            if conn:
                conn.close()

    # Insert, Update, Delete operations (same as your previous functions)
    def insert_flight(departure_date, departure_time, arrival_date, arrival_time, status, total_seats, economy_price, business_price, price_last_updated, pilot_id, departure_airport, destination_airport, airplane_id):
        conn = None  # Initialize conn before the try block
        try:
            # Debug: Log input data
            #print(f"Raw Inputs: {departure_date}, {departure_time}, {arrival_date}, {arrival_time}, {status}, {total_seats}, {economy_price}, {business_price}, {price_last_updated}, {pilot_id}, {departure_airport}, {destination_airport}, {airplane_id}")

            # Convert dates into datetime objects (Day/Month/Year format)
            departure_date_obj = datetime.strptime(departure_date.strip(), '%d/%m/%Y').date()
            arrival_date_obj = datetime.strptime(arrival_date.strip(), '%d/%m/%Y').date()
            price_last_updated_obj = datetime.strptime(price_last_updated.strip(), '%d/%m/%Y').date()

            # Validate and parse departure_time
            departure_time_str = departure_time_var.get().strip()
            if not departure_time_str:
                raise ValueError("Departure time cannot be empty.")
            try:
                departure_time_obj = datetime.strptime(departure_time_str.strip(), '%H').time()
            except ValueError:
                raise ValueError(f"Invalid departure time format: {departure_time_str}. Expected format is HH.")

            # Validate and parse arrival_time
            arrival_time_str = arrival_time_var.get().strip()
            if not arrival_time_str:
                raise ValueError("Arrival time cannot be empty.")
            try:
                arrival_time_obj = datetime.strptime(arrival_time_str.strip(), '%H').time()
            except ValueError:
                raise ValueError(f"Invalid arrival time format: {arrival_time_str}. Expected format is HH.")

            # Validate numeric fields
            try:
                total_seats = int(total_seats.strip())
            except ValueError:
                raise ValueError(f"Invalid total seats: {total_seats}")

            try:
                economy_price = int(economy_price.strip())
            except ValueError:
                raise ValueError(f"Invalid economy price: {economy_price}")

            try:
                business_price = int(business_price.strip())
            except ValueError:
                raise ValueError(f"Invalid business price: {business_price}")

            # Extract IDs from dropdown inputs
            try:
                pilot_id_cleaned = pilot_id.split(" - ")[0].strip()
            except IndexError:
                raise ValueError(f"Invalid pilot ID: {pilot_id}")

            try:
                departure_airport_cleaned = departure_airport.split(" - ")[0].strip()
            except IndexError:
                raise ValueError(f"Invalid departure airport: {departure_airport}")

            try:
                destination_airport_cleaned = destination_airport.split(" - ")[0].strip()
            except IndexError:
                raise ValueError(f"Invalid destination airport: {destination_airport}")

            try:
                airplane_id_cleaned = airplane_id.split(" - ")[0].strip()
            except IndexError:
                raise ValueError(f"Invalid airplane ID: {airplane_id}")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Flight 
                    (departure_date, departure_time, arrival_date, arrival_time, status, total_seats, economy_price, business_price, price_last_updated, pilot_id, departure_airport, destination_airport, airplane_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    departure_date_obj, departure_time_obj, arrival_date_obj, arrival_time_obj, status.strip(), total_seats,
                    economy_price, business_price, price_last_updated_obj,
                    pilot_id_cleaned, departure_airport_cleaned, destination_airport_cleaned, airplane_id_cleaned
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Flight added successfully!")
        except Exception as e:
            # Log the error in the console and show an error message
            print(f"Error details: {e}")
            messagebox.showerror("Error", f"Error inserting flight: {str(e)}")
            admin_dashboard()
        finally:
            if conn:  # Close the connection if it was established
                conn.close()



    def validate_date(date_string):
        # Validate if the date is in dd/mm/yyyy format
        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def validate_time(time_string):
        # Validate if the time is in HH:mm format
        time_pattern = r"^(?:[01]?\d|2[0-3]):([0-5]?\d)$"
        return re.match(time_pattern, time_string) is not None

    def update_flight():
        # Check if a flight is selected in the table
        selected_item = flight_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No flight selected.")
            admin_dashboard()
            return

        # Get the selected flight's data
        flight_data = flight_table.item(selected_item[0], "values")
        flight_id_to_update = flight_data[0]  # Assuming the first column is Flight ID

        # Build the update query dynamically
        updates = []
        params = []

        # Validate and parse dates
        if departure_date.get():
            if not validate_date(departure_date.get()):
                messagebox.showwarning("Warning", "Invalid departure date format. Use dd/mm/yyyy.")
                admin_dashboard()
                return
            departure_date_obj = datetime.strptime(departure_date.get(), "%d/%m/%Y").date()
            updates.append("departure_date = %s")
            params.append(departure_date_obj)

        if arrival_date.get():
            if not validate_date(arrival_date.get()):
                messagebox.showwarning("Warning", "Invalid arrival date format. Use dd/mm/yyyy.")
                admin_dashboard()
                return
            arrival_date_obj = datetime.strptime(arrival_date.get(), "%d/%m/%Y").date()
            updates.append("arrival_date = %s")
            params.append(arrival_date_obj)

        # Validate and parse times (Ensure the time is in HH:MM format)
        if departure_time_var.get():
            departure_time_raw = departure_time_var.get()
            if not validate_time(departure_time_raw):
                messagebox.showwarning("Warning", "Invalid departure time format. Use HH:mm.")
                admin_dashboard()
                return
            # Extract the hour part (HH) from the "HH:mm" format
            hour, _ = departure_time_raw.split(":")
            departure_time_obj = f"{int(hour):02d}:00"  # Format as HH:00
            updates.append("departure_time = %s")
            params.append(departure_time_obj)

        # Validate and parse arrival time
        if arrival_time_var.get():
            arrival_time_raw = arrival_time_var.get()
            if not validate_time(arrival_time_raw):
                messagebox.showwarning("Warning", "Invalid arrival time format. Use HH:mm.")
                admin_dashboard()
                return
            # Extract the hour part (HH) from the "HH:mm" format
            hour, _ = arrival_time_raw.split(":")
            arrival_time_obj = f"{int(hour):02d}:00"  # Format as HH:00
            updates.append("arrival_time = %s")
            params.append(arrival_time_obj)

        # Check each other input field and add to the update list if provided
        if status.get():
            updates.append("status = %s")
            params.append(status.get())
        if total_seats.get():
            updates.append("total_seats = %s")
            params.append(total_seats.get())
        if economy_price.get():
            updates.append("economy_price = %s")
            params.append(economy_price.get())
        if business_price.get():
            updates.append("business_price = %s")
            params.append(business_price.get())
        if price_last_updated.get():
            updates.append("price_last_updated = %s")
            params.append(price_last_updated.get())
        if selected_pilot.get():
            updates.append("pilot_id = %s")
            params.append(selected_pilot.get())
        if selected_airplane.get():
            updates.append("airplane_id = %s")
            params.append(selected_airplane.get())
        if selected_departure_airport.get():
            updates.append("departure_airport = %s")
            params.append(selected_departure_airport.get())
        if selected_arrival_airport.get():
            updates.append("arrival_airport = %s")
            params.append(selected_arrival_airport.get())

        # Ensure at least one field is being updated
        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            return

        # Add the flight ID to the parameters
        params.append(flight_id_to_update)

        # Create the dynamic SQL query
        update_query = f"UPDATE Flight SET {', '.join(updates)} WHERE flight_id = %s"

        try:
            # Connect to the database and execute the query
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            # Show success message and reload the table
            messagebox.showinfo("Success", f"Flight ID {flight_id_to_update} updated successfully!")
            load_flights()
            admin_dashboard()
        except Exception as e:
            # Show error message if any exception occurs
            messagebox.showerror("Error", f"Error updating flight: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    def delete_flight():
        selected_item = flight_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a flight to delete")
            admin_dashboard()
            return

        flight_id = flight_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete flight ID {flight_id}? This will remove related bookings.")
        if not confirm:
            admin_dashboard()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Flight WHERE flight_id = %s", (flight_id,))
                conn.commit()

                messagebox.showinfo("Success", "Flight deleted successfully!")
                load_flights()
                admin_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Error deleting flight: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    # Label and Entry Widgets for inserting and updating flights (grouped in two columns)
    #tk.Label(manage_frame, text="Manage Flights", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)

    # Create entry widgets for each field
    departure_date_entry = DateEntry(manage_frame, textvariable=departure_date, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yyyy")
    arrival_date_entry = DateEntry(manage_frame, textvariable=arrival_date, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern="dd/mm/yyyy")
    status_entry = tk.Entry(manage_frame)
    total_seats_entry = tk.Entry(manage_frame)
    flight_class_entry = tk.Entry(manage_frame)
    gate_number_entry = tk.Entry(manage_frame)
    economy_price_entry = tk.Entry(manage_frame)
    business_price_entry = tk.Entry(manage_frame)
    price_last_updated_entry = tk.Entry(manage_frame)
    pilot_id_entry = tk.Entry(manage_frame)
    departure_airport_entry = tk.Entry(manage_frame)
    arrival_airport_entry = tk.Entry(manage_frame)
    airplane_id_entry = tk.Entry(manage_frame)

    # Group labels and entries in two columns
    labels = [
        ("Departure Date:", departure_date_entry),
        ("Arrival Date:", arrival_date_entry),
        ("Status:", status_entry),
        ("Total Seats:", total_seats_entry),
        ("Flight Class:", flight_class_entry),
        ("Gate Number:", gate_number_entry),
        ("Economy Price:", economy_price_entry),
        ("Business Price:", business_price_entry),
        ("Price Last Updated:", price_last_updated_entry),
        ("Pilot ID:", pilot_id_entry),
        ("Departure Airport:", departure_airport_entry),
        ("Arrival Airport:", arrival_airport_entry),
        ("Airplane ID:", airplane_id_entry)
    ]
    # Create variables for Spinbox inputs
    # Initialize empty StringVars for date and time fields
    departure_date = tk.StringVar(value="")  # Empty by default
    arrival_date = tk.StringVar(value="")    # Empty by default
    departure_time_var = tk.StringVar(value="")  # Empty by default
    arrival_time_var = tk.StringVar(value="")    # Empty by default

    # Display labels and entry widgets in a grid
    tk.Label(manage_frame, text="Manage Flights", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Departure Date
    tk.Label(manage_frame, text="Departure Date:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    departure_date_entry = DateEntry(
        manage_frame, textvariable=departure_date, width=12, 
        background="darkblue", foreground="white", borderwidth=2, 
        date_pattern="dd/mm/yyyy"
    )
    departure_date_entry.delete(0, "end")  # Make sure the field is empty
    departure_date_entry.grid(row=1, column=1, padx=5, pady=2)

    # Bind the DateEntry to detect clearing
    departure_date_entry.bind("<KeyRelease>", lambda event: clear_date_if_empty(event, departure_date))

    # Departure Time
    departure_time_label = tk.Label(manage_frame, text="Departure Time:", bg="white")
    departure_time_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

    departure_time_entry = tk.Spinbox(
        manage_frame, from_=0, to=23, width=5, format="%02.0f", 
        textvariable=departure_time_var
    )
    departure_time_entry.delete(0, "end")  # Ensure the field is empty
    departure_time_entry.grid(row=2, column=1, padx=5, pady=2)

    # Bind the Spinbox to detect clearing
    departure_time_entry.bind("<KeyRelease>", lambda event: clear_date_if_empty(event, departure_time_var))

    # Arrival Date
    tk.Label(manage_frame, text="Arrival Date:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    arrival_date_entry = DateEntry(
        manage_frame, textvariable=arrival_date, width=12, 
        background="darkblue", foreground="white", borderwidth=2, 
        date_pattern="dd/mm/yyyy"
    )
    arrival_date_entry.delete(0, "end")  # Make sure the field is empty
    arrival_date_entry.grid(row=3, column=1, padx=5, pady=2)

    # Bind the DateEntry to detect clearing
    arrival_date_entry.bind("<KeyRelease>", lambda event: clear_date_if_empty(event, arrival_date))

    # Arrival Time
    arrival_time_label = tk.Label(manage_frame, text="Arrival Time:", bg="white")
    arrival_time_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")

    arrival_time_entry = tk.Spinbox(
        manage_frame, from_=0, to=23, width=5, format="%02.0f", 
        textvariable=arrival_time_var
    )
    arrival_time_entry.delete(0, "end")  # Ensure the field is empty
    arrival_time_entry.grid(row=4, column=1, padx=5, pady=2)
    # Bind the Spinbox to detect clearing
    arrival_time_entry.bind("<KeyRelease>", lambda event: clear_date_if_empty(event, arrival_time_var))

    # Status
    tk.Label(manage_frame, text="Status:", bg="white").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, status, "Scheduled", "Delayed", "Cancelled").grid(row=5, column=1, padx=5, pady=2)
    # Total Seats
    tk.Label(manage_frame, text="Total Seats:", bg="white").grid(row=6, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=total_seats).grid(row=6, column=1, padx=5, pady=2)

    # Economy Price
    tk.Label(manage_frame, text="Economy Price:", bg="white").grid(row=7, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=economy_price).grid(row=7, column=1, padx=5, pady=2)

    # Business Price
    tk.Label(manage_frame, text="Business Price:", bg="white").grid(row=1, column=2, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=business_price).grid(row=1, column=3, padx=5, pady=2)

    # Price Last Updated
    tk.Label(manage_frame, text="Price Last Updated:", bg="white").grid(row=2, column=2, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=price_last_updated).grid(row=2, column=3, padx=5, pady=2)

    # Pilot
    tk.Label(manage_frame, text="Pilot:", bg="white").grid(row=3, column=2, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, selected_pilot, *pilots).grid(row=3, column=3, padx=5, pady=2)

    # Departure Airport
    tk.Label(manage_frame, text="Departure Airport:", bg="white").grid(row=4, column=2, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, selected_departure_airport, *airports).grid(row=4, column=3, padx=5, pady=2)

    # Arrival Airport
    tk.Label(manage_frame, text="Arrival Airport:", bg="white").grid(row=5, column=2, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, selected_arrival_airport, *airports).grid(row=5, column=3, padx=5, pady=2)

    # Airplane
    tk.Label(manage_frame, text="Airplane:", bg="white").grid(row=6, column=2, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, selected_airplane, *airplanes).grid(row=6, column=3, padx=5, pady=2)

    # Flight Information Title
    tk.Label(manage_frame, text="Flight Information", font=("Arial", 18, "bold"), bg="white").grid(row=8, column=0, columnspan=4, pady=20, sticky="w")


    
    # Add buttons to insert flights, update flights, etc.
    #tk.Button(manage_frame, text="Add Flight", command=lambda: insert_flight(departure_date.get(), arrival_date.get(), status.get(), total_seats.get(), flight_class.get(), gate_number.get(), economy_price.get(), business_price.get(), price_last_updated.get(), selected_pilot.get(), selected_departure_airport.get(), selected_arrival_airport.get(), selected_airplane.get())).grid(row=8, column=0, columnspan=4, pady=20)

    # Buttons in a horizontal line below the table
    button_frame = tk.Frame(manage_frame, bg="white")
    button_frame.grid(row=10, column=0, columnspan=4, pady=10)

    #def insert_flight(departure_date, departure_time, arrival_date, arrival_time, status, total_seats, flight_class, gate_number, economy_price, business_price, price_last_updated, pilot_id, departure_airport, destination_airport, airplane_id):

    tk.Button(button_frame, text="Insert Flight", command=lambda: insert_flight(departure_date.get(), departure_time.get(), arrival_date.get(), arrival_time.get(), status.get(), total_seats.get(), economy_price.get(), business_price.get(), price_last_updated.get(), selected_pilot.get(), selected_departure_airport.get(), selected_arrival_airport.get(), selected_airplane.get()), bg="blue", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Update Flight", command=update_flight, bg="green", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Delete Flight", command=delete_flight, bg="red", fg="white").grid(row=0, column=2, padx=5)


   # Create a treeview to display all flights with reduced row and column sizes
    flight_table = ttk.Treeview(manage_frame, columns=("flight_id", "departure_date", "departure_time", "arrival_date", "arrival_time", "status",
                                                    "total_seats", "economy_price", "business_price",
                                                    "price_last_updated", "pilot_id", "departure_airport",
                                                    "arrival_airport", "airplane_id"), show="headings", height=15)

    flight_table.grid(row=9, column=0, columnspan=4, pady=20)

    # Define columns and headings with smaller column width
    for col in flight_table["columns"]:
        flight_table.heading(col, text=col.replace("_", " ").title())
        flight_table.column(col, width=100, anchor="center")

    # Create a vertical scrollbar for the Treeview
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=flight_table.yview)
    scrollbar.grid(row=9, column=4, sticky="ns")  # Position scrollbar next to the treeview

    # Configure the treeview to work with the scrollbar
    flight_table.configure(yscrollcommand=scrollbar.set)


    # Load the flight data into the table
    load_flights()
    # Function to handle clearing of fields
    def clear_date_if_empty(event, field_var):
        """
        This function checks if the field's value is empty. 
        If empty, it resets the associated StringVar to an empty string.
        """
        if event.widget.get() == "":
            field_var.set("")

    # Close the manage window when switching to another dashboard button
    def close_manage_window():
        if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
            parent_frame.manage_window.destroy()

    # Assuming you have a function to switch to another section in the dashboard
    tk.Button(parent_frame, text="Switch to Another Section", command=close_manage_window).pack()

def manage_pilot(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Pilot")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage pilots window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    pilot_name = tk.StringVar()
    pilot_address = tk.StringVar()
    pilot_contact_number = tk.StringVar()
    pilot_salary = tk.StringVar()
    pilot_medical_exam_date = tk.StringVar()

    # Table for displaying pilots
    def load_pilots():
        # Clear the table before loading new data
        for item in pilot_table.get_children():
            pilot_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Pilot")  # Load all pilots
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    pilot_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading pilots: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Insert Pilot
    def insert_pilot():
        conn = None
        try:
            # Validate and parse fields
            if not pilot_name.get().strip() or not pilot_address.get().strip() or not pilot_contact_number.get().strip() or not pilot_salary.get().strip() or not pilot_medical_exam_date.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Pilot 
                    (name, address, contact_number, salary, medical_exam_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    pilot_name.get().strip(), pilot_address.get().strip(), pilot_contact_number.get().strip(),
                    pilot_salary.get().strip(), pilot_medical_exam_date.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Pilot added successfully!")
                load_pilots()  # Reload the table
                admin_dashboard()
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting pilot: {str(e)}")
        finally:
            if conn:
                conn.close()

    # Update Pilot
    def update_pilot():
        # Check if a pilot is selected in the table
        selected_item = pilot_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No pilot selected.")
            return

        pilot_data = pilot_table.item(selected_item[0], "values")
        pilot_id_to_update = pilot_data[0]  # Assuming the first column is Pilot ID

        # Prepare updated data
        updates = []
        params = []

        if pilot_name.get():
            updates.append("name = %s")
            params.append(pilot_name.get().strip())
        if pilot_address.get():
            updates.append("address = %s")
            params.append(pilot_address.get().strip())
        if pilot_contact_number.get():
            updates.append("contact_number = %s")
            params.append(pilot_contact_number.get().strip())
        if pilot_salary.get():
            updates.append("salary = %s")
            params.append(pilot_salary.get().strip())
        if pilot_medical_exam_date.get():
            updates.append("medical_exam_date = %s")
            params.append(pilot_medical_exam_date.get().strip())

        # Ensure at least one field is being updated
        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            open_crew_management_window()
            return

        # Add the pilot ID to the parameters
        params.append(pilot_id_to_update)

        # Create the dynamic SQL query
        update_query = f"UPDATE Pilot SET {', '.join(updates)} WHERE pilot_id = %s"

        try:
            # Connect to the database and execute the query
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            # Show success message and reload the table
            messagebox.showinfo("Success", f"Pilot ID {pilot_id_to_update} updated successfully!")
            load_pilots()
            admin_dashboard()
            open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating pilot: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Delete Pilot
    def delete_pilot():
        selected_item = pilot_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a pilot to delete")
            return

        pilot_id = pilot_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Pilot ID {pilot_id}?")
        if not confirm:
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Pilot WHERE pilot_id = %s", (pilot_id,))
                conn.commit()

                messagebox.showinfo("Success", "Pilot deleted successfully!")
                load_pilots()
                admin_dashboard()
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting pilot: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Pilot", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=pilot_name).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Address:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=pilot_address).grid(row=2, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Contact Number:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=pilot_contact_number).grid(row=3, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Salary:", bg="white").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=pilot_salary).grid(row=4, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Medical Exam Date:", bg="white").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=pilot_medical_exam_date).grid(row=5, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Pilot Information:", font=("Arial", 18, "bold"), bg="white").grid(row=6, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all pilots
    pilot_table = ttk.Treeview(manage_frame, columns=("pilot_id", "name", "address", "contact_number", "salary", "medical_exam_date"), show="headings")
    pilot_table.grid(row=7, column=0, columnspan=4, padx=10, pady=10)

    # Define headings
    pilot_table.heading("pilot_id", text="Pilot ID")
    pilot_table.heading("name", text="Name")
    pilot_table.heading("address", text="Address")
    pilot_table.heading("contact_number", text="Contact Number")
    pilot_table.heading("salary", text="Salary")
    pilot_table.heading("medical_exam_date", text="Medical Exam Date")

    # Define columns and headings with smaller column width
    for col in pilot_table["columns"]:
        pilot_table.heading(col, text=col.replace("_", " ").title())
        pilot_table.column(col, width=150, anchor="center")

    # Create a vertical scrollbar for the Treeview
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=pilot_table.yview)
    scrollbar.grid(row=7, column=4, sticky="ns")  # Position scrollbar next to the treeview

    # Configure the treeview to work with the scrollbar
    pilot_table.configure(yscrollcommand=scrollbar.set)

    # Buttons in a horizontal line below the table
    button_frame = tk.Frame(manage_frame, bg="white")
    button_frame.grid(row=8, column=0, columnspan=4, pady=10)

    tk.Button(button_frame, text="Insert Pilot", command=insert_pilot, bg="blue", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Update Pilot", command=update_pilot, bg="green", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Delete Pilot", command=delete_pilot, bg="red", fg="white").grid(row=0, column=2, padx=5)

    # Load pilots into the table
    load_pilots()

def manage_technician(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Technician")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage technicians window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    technician_name = tk.StringVar()
    technician_address = tk.StringVar()
    technician_contact_number = tk.StringVar()
    technician_salary = tk.StringVar()
    technician_expertise = tk.StringVar()  # New field for expertise

    # Table for displaying technicians
    def load_technicians():
        # Clear the table before loading new data
        for item in technician_table.get_children():
            technician_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Technician")  # Load all technicians
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    technician_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading technicians: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Insert Technician
    def insert_technician():
        conn = None
        try:
            # Validate and parse fields
            if not technician_name.get().strip() or not technician_address.get().strip() or not technician_contact_number.get().strip() or not technician_salary.get().strip() or not technician_expertise.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO Technician 
                    (name, address, contact_number, salary, expertise)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    technician_name.get().strip(), technician_address.get().strip(), technician_contact_number.get().strip(),
                    technician_salary.get().strip(), technician_expertise.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Technician added successfully!")
                load_technicians()
                admin_dashboard()  # Reload the table
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting technician: {str(e)}")
            admin_dashboard()  # Reload the table
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Update Technician
    def update_technician():
        # Check if a technician is selected in the table
        selected_item = technician_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No technician selected.")
            return

        technician_data = technician_table.item(selected_item[0], "values")
        technician_id_to_update = technician_data[0]  # Assuming the first column is Technician ID

        # Prepare updated data
        updates = []
        params = []

        if technician_name.get():
            updates.append("name = %s")
            params.append(technician_name.get().strip())
        if technician_address.get():
            updates.append("address = %s")
            params.append(technician_address.get().strip())
        if technician_contact_number.get():
            updates.append("contact_number = %s")
            params.append(technician_contact_number.get().strip())
        if technician_salary.get():
            updates.append("salary = %s")
            params.append(technician_salary.get().strip())
        if technician_expertise.get():
            updates.append("expertise = %s")
            params.append(technician_expertise.get().strip())

        # Ensure at least one field is being updated
        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()  # Reload the table
            open_crew_management_window()
            return

        # Add the technician ID to the parameters
        params.append(technician_id_to_update)

        # Create the dynamic SQL query
        update_query = f"UPDATE Technician SET {', '.join(updates)} WHERE technician_id = %s"

        try:
            # Connect to the database and execute the query
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            # Show success message and reload the table
            messagebox.showinfo("Success", f"Technician ID {technician_id_to_update} updated successfully!")
            load_technicians()
            admin_dashboard()
            open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating technician: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Delete Technician
    def delete_technician():
        selected_item = technician_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a technician to delete")
            admin_dashboard()
            open_crew_management_window()
            return

        technician_id = technician_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Technician ID {technician_id}?")
        if not confirm:
            admin_dashboard()
            open_crew_management_window()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Technician WHERE technician_id = %s", (technician_id,))
                conn.commit()

                messagebox.showinfo("Success", "Technician deleted successfully!")
                load_technicians()
                admin_dashboard()
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting technician: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Technician", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=technician_name).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Address:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=technician_address).grid(row=2, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Contact Number:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=technician_contact_number).grid(row=3, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Salary:", bg="white").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=technician_salary).grid(row=4, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Expertise:", bg="white").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=technician_expertise).grid(row=5, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Technician Information:", font=("Arial", 18, "bold"), bg="white").grid(row=6, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all technicians
    technician_table = ttk.Treeview(manage_frame, columns=("technician_id", "name", "address", "contact_number", "salary", "expertise"), show="headings")
    technician_table.grid(row=7, column=0, columnspan=4, padx=10, pady=10)

    # Define headings
    technician_table.heading("technician_id", text="Technician ID")
    technician_table.heading("name", text="Name")
    technician_table.heading("address", text="Address")
    technician_table.heading("contact_number", text="Contact Number")
    technician_table.heading("salary", text="Salary")
    technician_table.heading("expertise", text="Expertise")

    # Define columns and headings with smaller column width
    for col in technician_table["columns"]:
        technician_table.heading(col, text=col.replace("_", " ").title())
        technician_table.column(col, width=150, anchor="center")

    # Create a vertical scrollbar for the Treeview
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=technician_table.yview)
    scrollbar.grid(row=7, column=4, sticky="ns")  # Position scrollbar next to the treeview

    # Configure the treeview to work with the scrollbar
    technician_table.configure(yscrollcommand=scrollbar.set)

    # Buttons in a horizontal line below the table
    button_frame = tk.Frame(manage_frame, bg="white")
    button_frame.grid(row=8, column=0, columnspan=5, pady=10)

    tk.Button(button_frame, text="Add Technician", command=insert_technician).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Update Technician", command=update_technician).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Delete Technician", command=delete_technician).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Refresh", command=load_technicians).grid(row=0, column=3, padx=5)

    load_technicians()  # Populate the table with technicians

def fetch_flights():
    """
    Fetch only the flight_id from the Flight table.
    """
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            # Query to fetch only the flight_id
            cursor.execute("SELECT flight_id FROM Flight")
            flights = cursor.fetchall()
            # Return flight IDs as a simple list
            return [str(flight_id[0]) for flight_id in flights]
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching flights: {str(e)}")
    finally:
        if conn:
            conn.close()
    return []

def fetch_roles():
    # Fetch predefined roles for crew members
    return ["Co-Pilot", "Flight Attendant", "Engineer"]

def manage_crew_member(parent_frame):
    print("Opening Crew Member Management...")

    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Crew Member")
    manage_window.geometry("1000x700+450+70")  # Adjusted window size
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage crew member window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    crew_member_name = tk.StringVar()
    crew_member_role = tk.StringVar()
    crew_member_flight_id = tk.StringVar()
    crew_member_contact_number = tk.StringVar()

    # Dropdown for flights
    available_flights = fetch_flights()
    tk.Label(manage_frame, text="Flight ID:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    flight_dropdown = ttk.Combobox(manage_frame, textvariable=crew_member_flight_id, values=available_flights, state="readonly")
    flight_dropdown.grid(row=3, column=1, padx=5, pady=2)

    # Dropdown for roles
    available_roles = fetch_roles()
    tk.Label(manage_frame, text="Role:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    role_dropdown = ttk.Combobox(manage_frame, textvariable=crew_member_role, values=available_roles, state="readonly")
    role_dropdown.grid(row=2, column=1, padx=5, pady=2)

    # Table for displaying crew members
    def load_crew_members():
        # Clear the table before loading new data
        for item in crew_member_table.get_children():
            crew_member_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM CrewMember")  # Load all crew members
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    crew_member_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading crew members: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Insert Crew Member
    def insert_crew_member():
        conn = None
        try:
            # Validate and parse fields
            if not crew_member_name.get().strip() or not crew_member_role.get().strip() or not crew_member_flight_id.get().strip() or not crew_member_contact_number.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO CrewMember 
                    (name, role, flight_id, contact_number)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    crew_member_name.get().strip(),
                    crew_member_role.get().strip(),
                    crew_member_flight_id.get().split(" - ")[0],  # Extract flight ID
                    crew_member_contact_number.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Crew Member added successfully!")
                load_crew_members()  # Reload the table
                admin_dashboard()
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error inserting crew member: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    # Update Crew Member
    def update_crew_member():
        selected_item = crew_member_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a crew member to update")
            return

        crew_member_id = crew_member_table.item(selected_item, "values")[0]

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Update query
                query = """
                    UPDATE CrewMember
                    SET name = %s, role = %s, flight_id = %s, contact_number = %s
                    WHERE crew_member_id = %s
                """
                cursor.execute(query, (
                    crew_member_name.get().strip(),
                    crew_member_role.get().strip(),
                    crew_member_flight_id.get().split(" - ")[0],  # Extract flight ID
                    crew_member_contact_number.get().strip(),
                    crew_member_id
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Crew Member updated successfully!")
                load_crew_members()
                admin_dashboard()
                open_crew_management_window()  # Reload the table
        except Exception as e:
            messagebox.showerror("Error", f"Error updating crew member: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Delete Crew Member
    def delete_crew_member():
        selected_item = crew_member_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a crew member to delete")
            return

        crew_member_id = crew_member_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Crew Member ID {crew_member_id}?")
        if not confirm:
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM CrewMember WHERE crew_member_id = %s", (crew_member_id,))
                conn.commit()

                messagebox.showinfo("Success", "Crew Member deleted successfully!")
                load_crew_members()
                admin_dashboard()
                open_crew_management_window()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting crew member: {str(e)}")
            admin_dashboard()
            open_crew_management_window()
        finally:
            if conn:
                conn.close()

    # Title of the form
    tk.Label(manage_frame, text="Manage Crew Member", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=crew_member_name).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Contact Number:", bg="white").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=crew_member_contact_number).grid(row=4, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Crew Member Information:", font=("Arial", 18, "bold"), bg="white").grid(row=5, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all crew members
    crew_member_table = ttk.Treeview(manage_frame, columns=("crew_member_id", "name", "role", "flight_id", "contact_number"), show="headings")
    crew_member_table.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

    # Define headings
    crew_member_table.heading("crew_member_id", text="Crew Member ID")
    crew_member_table.heading("name", text="Name")
    crew_member_table.heading("role", text="Role")
    crew_member_table.heading("flight_id", text="Flight ID")
    crew_member_table.heading("contact_number", text="Contact Number")

    # Define columns and headings with smaller column width
    for col in crew_member_table["columns"]:
        crew_member_table.heading(col, text=col.replace("_", " ").title())
        crew_member_table.column(col, width=150, anchor="center")

    # Create a vertical scrollbar for the Treeview
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=crew_member_table.yview)
    scrollbar.grid(row=6, column=4, sticky="ns")  # Position scrollbar next to the treeview

    # Configure the treeview to work with the scrollbar
    crew_member_table.configure(yscrollcommand=scrollbar.set)

    # Buttons in a horizontal line below the table
    button_frame = tk.Frame(manage_frame, bg="white")
    button_frame.grid(row=7, column=0, columnspan=5, pady=10)

    tk.Button(button_frame, text="Add Crew Member", command=insert_crew_member).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Update Crew Member", command=update_crew_member).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Delete Crew Member", command=delete_crew_member).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Refresh", command=load_crew_members).grid(row=0, column=3, padx=5)

    load_crew_members()  # Populate the table with crew members

def open_crew_management_window():
    # Create a new top-level window
    crew_window = tk.Toplevel()
    crew_window.title("Crew Management")
    crew_window.geometry("1450x800+25+25")
    
    tk.Label(crew_window, text="Manage crew", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")
    
    # Create buttons for managing different crew categories
    tk.Button(crew_window, text="Manage Pilot", font=("Arial", 20), command=lambda: manage_pilot(crew_window)).place(relx=0.05, rely=0.15, anchor="w")
    tk.Button(crew_window, text="Manage Technician", font=("Arial", 20), command=lambda: manage_technician(crew_window)).place(relx=0.05, rely=0.25, anchor="w")
    tk.Button(crew_window, text="Manage Crew Member", font=("Arial", 20), command=lambda: manage_crew_member(crew_window)).place(relx=0.05, rely=0.35, anchor="w")
    tk.Button(crew_window, text="Exit", font=("Arial", 20), command=crew_window.destroy).place(relx=0.05, rely=0.85, anchor="w")
    
def manage_passenger(parent_frame):
    # Close the window if it's already open
    if hasattr(parent_frame, 'manage_window') and parent_frame.manage_window.winfo_exists():
        parent_frame.manage_window.destroy()

    # Create a new top-level window
    manage_window = tk.Toplevel(parent_frame)
    manage_window.title("Manage Passenger")
    manage_window.geometry("1100x700+400+100")  # Adjusted window size for better table display
    manage_window.resizable(True, True)

    # Store the reference of the window to close it later
    parent_frame.manage_window = manage_window

    # Create a frame for the manage passengers window
    manage_frame = tk.Frame(manage_window, bg="white")
    manage_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Entry Widgets
    username = tk.StringVar()
    name = tk.StringVar()
    surname = tk.StringVar()
    password = tk.StringVar()
    contact_number = tk.StringVar()
    role = tk.StringVar()
    email = tk.StringVar()

    # Table for displaying passengers
    def load_passengers():
        # Clear the table before loading new data
        for item in passenger_table.get_children():
            passenger_table.delete(item)

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM User WHERE role='Passenger'")  # Load only passengers
                rows = cursor.fetchall()

                # Insert rows into the table
                for row in rows:
                    passenger_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading passengers: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    # Insert Passenger
    def insert_passenger():
        conn = None
        try:
            # Validate and parse fields
            if not username.get().strip() or not name.get().strip() or not surname.get().strip() or not password.get().strip() or not email.get().strip():
                raise ValueError("All fields are required")

            # Establish database connection
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()

                # Insert query
                query = """
                    INSERT INTO User 
                    (username, name, surname, password, contact_number, role, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    username.get().strip(), name.get().strip(), surname.get().strip(),
                    password.get().strip(), contact_number.get().strip(), role.get().strip(), email.get().strip()
                ))
                conn.commit()

                # Success message
                messagebox.showinfo("Success", "Passenger added successfully!")
                load_passengers()
                admin_dashboard()  # Reload the table
        except Exception as e:
            # Log the error in the console and show an error message
            messagebox.showerror("Error", f"Error inserting passenger: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    # Update Passenger
    def update_passenger():
        # Check if a passenger is selected in the table
        selected_item = passenger_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No passenger selected.")
            return

        passenger_data = passenger_table.item(selected_item[0], "values")
        passenger_id_to_update = passenger_data[0]  # Assuming the first column is User ID

        # Prepare updated data
        updates = []
        params = []

        if username.get():
            updates.append("username = %s")
            params.append(username.get().strip())
        if name.get():
            updates.append("name = %s")
            params.append(name.get().strip())
        if surname.get():
            updates.append("surname = %s")
            params.append(surname.get().strip())
        if password.get():
            updates.append("password = %s")
            params.append(password.get().strip())
        if contact_number.get():
            updates.append("contact_number = %s")
            params.append(contact_number.get().strip())
        if email.get():
            updates.append("email = %s")
            params.append(email.get().strip())

        # Ensure at least one field is being updated
        if not updates:
            messagebox.showwarning("Warning", "No fields provided for update.")
            admin_dashboard()
            return

        # Add the user ID to the parameters
        params.append(passenger_id_to_update)

        # Create the dynamic SQL query
        update_query = f"UPDATE User SET {', '.join(updates)} WHERE user_id = %s"

        try:
            # Connect to the database and execute the query
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute(update_query, params)
            conn.commit()

            # Show success message and reload the table
            messagebox.showinfo("Success", f"Passenger ID {passenger_id_to_update} updated successfully!")
            load_passengers()
            admin_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating passenger: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()

    # Delete Passenger
    def delete_passenger():
        selected_item = passenger_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a passenger to delete")
            admin_dashboard()
            return

        passenger_id = passenger_table.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Passenger ID {passenger_id}? This will remove related bookings.")
        if not confirm:
            admin_dashboard()
            return

        try:
            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM User WHERE user_id = %s", (passenger_id,))
                conn.commit()

                messagebox.showinfo("Success", "Passenger deleted successfully!")
                load_passengers()
                admin_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting passenger: {str(e)}")
            admin_dashboard()
        finally:
            if conn:
                conn.close()
    # Title of the form
    tk.Label(manage_frame, text="Manage Passenger", font=("Arial", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=8, pady=10, sticky="w")

    # Create entry widgets for each field
    tk.Label(manage_frame, text="User Name:", bg="white").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=username).grid(row=1, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Name:", bg="white").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=name).grid(row=2, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Surname:", bg="white").grid(row=3, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=surname).grid(row=3, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Password:", bg="white").grid(row=4, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=password, show="*").grid(row=4, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Contact Number:", bg="white").grid(row=5, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=contact_number).grid(row=5, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Email:", bg="white").grid(row=6, column=0, padx=5, pady=2, sticky="w")
    tk.Entry(manage_frame, textvariable=email).grid(row=6, column=1, padx=5, pady=2)

    tk.Label(manage_frame, text="Role:", bg="white").grid(row=7, column=0, padx=5, pady=2, sticky="w")
    tk.OptionMenu(manage_frame, role, "Admin", "Passenger").grid(row=7, column=1, padx=5, pady=2)

    # Title of the table
    tk.Label(manage_frame, text="Information Passenger:", font=("Arial", 18, "bold"), bg="white").grid(row=8, column=0, columnspan=8, pady=10, sticky="w")

    # Create a treeview to display all passengers
    passenger_table = ttk.Treeview(manage_frame, columns=("User_id", "username", "name", "surname", "password", "contact_number", "role", "email"), show="headings")
    passenger_table.grid(row=9, column=0, columnspan=4, padx=10, pady=10)

    # Define headings
    passenger_table.heading("User_id", text="User ID")
    passenger_table.heading("username", text="Username")
    passenger_table.heading("name", text="Name")
    passenger_table.heading("surname", text="Surname")
    passenger_table.heading("password", text="Password")
    passenger_table.heading("contact_number", text="Contact Number")
    passenger_table.heading("role", text="Role")
    passenger_table.heading("email", text="Email")

    # Define columns and headings with smaller column width
    for col in passenger_table["columns"]:
        passenger_table.heading(col, text=col.replace("_", " ").title())
        passenger_table.column(col, width=100, anchor="center")

    # Create a vertical scrollbar for the Treeview
    scrollbar = tk.Scrollbar(manage_frame, orient="vertical", command=passenger_table.yview)
    scrollbar.grid(row=9, column=4, sticky="ns")  # Position scrollbar next to the treeview

    # Configure the treeview to work with the scrollbar
    passenger_table.configure(yscrollcommand=scrollbar.set)

    # Buttons in a horizontal line below the table
    button_frame = tk.Frame(manage_frame, bg="white")
    button_frame.grid(row=10, column=0, columnspan=4, pady=10)

    tk.Button(button_frame, text="Insert Passenger", command=insert_passenger, bg="blue", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Update Passenger", command=update_passenger, bg="green", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Delete Passenger", command=delete_passenger, bg="red", fg="white").grid(row=0, column=2, padx=5)
    # Load passengers into the table
    load_passengers()

def view_bookings():
    # Create a new Tkinter window
    window = tk.Tk()
    window.title("View Bookings")

    # Add a title above the table
    title_label = tk.Label(window, text="Booking Information", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)  # Adds some padding around the title

    # Create a Treeview widget for displaying data in table format
    tree = ttk.Treeview(window, columns=("Booking ID", "Booking Date", "Passenger Name", "Passenger Email", 
                                         "Flight Info", "Seat Info", "Ticket Price", "Payment Info"), 
                        show="headings")

    # Define the headings (columns)
    tree.heading("Booking ID", text="Booking ID")
    tree.heading("Booking Date", text="Booking Date")
    tree.heading("Passenger Name", text="Passenger Name")
    tree.heading("Passenger Email", text="Passenger Email")
    tree.heading("Flight Info", text="Flight Info")
    tree.heading("Seat Info", text="Seat Info")
    tree.heading("Ticket Price", text="Ticket Price")
    tree.heading("Payment Info", text="Payment Info")

    # Set column width to fit the content
    tree.column("Booking ID", width=100)
    tree.column("Booking Date", width=150)
    tree.column("Passenger Name", width=150)
    tree.column("Passenger Email", width=200)
    tree.column("Flight Info", width=250)
    tree.column("Seat Info", width=150)
    tree.column("Ticket Price", width=100)
    tree.column("Payment Info", width=150)

    # Fetch the booking data from the database
    conn = connect_to_database()
    cursor = conn.cursor()
    query = """
    SELECT 
        b.booking_id,
        b.booking_date,
        u.name AS passenger_name,
        u.surname AS passenger_surname,
        u.email AS passenger_email,
        f.departure_airport,
        f.destination_airport,
        f.departure_date,
        f.arrival_date,
        s.seat_number,
        s.is_available,
        t.ticket_price,
        t.booking_status,
        p.payment_date,
        p.payment_method
    FROM 
        Booking b
    JOIN 
        User u ON b.user_id = u.user_id
    JOIN 
        Flight f ON b.flight_id = f.flight_id
    JOIN 
        Seat s ON f.flight_id = s.flight_id
    JOIN 
        Ticket t ON s.seat_id = t.seat_id
    JOIN 
        Payment p ON b.booking_id = p.booking_id
    ORDER BY 
        b.booking_date DESC;
    """
    cursor.execute(query)
    bookings = cursor.fetchall()

    # Add rows to the Treeview (table)
    for booking in bookings:
        booking_id, booking_date, passenger_name, passenger_surname, passenger_email, departure_airport, destination_airport, departure_date, arrival_date, seat_number, is_available, ticket_price, booking_status, payment_date, payment_method = booking

        # Format the Flight Info and Seat Info
        flight_info = f"{departure_airport} -> {destination_airport} ({departure_date} - {arrival_date})"
        seat_info = f"Seat {seat_number} ({'Available' if is_available else 'Not Available'})"
        payment_info = f"{payment_date} ({payment_method})"

        # Insert a new row into the Treeview
        tree.insert("", "end", values=(booking_id, booking_date, f"{passenger_name} {passenger_surname}", 
                                      passenger_email, flight_info, seat_info, ticket_price, payment_info))

    # Place the Treeview widget on the window
    tree.pack(expand=True, fill=tk.BOTH)