from database import connect_to_database
from utils import fetch_airports , set_background
from tkcalendar import Calendar
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import os
from PIL import Image, ImageTk

def passenger_signup_window():
    # Create the signup window
    signup_window = tk.Tk()
    signup_window.title("Passenger Signup")

    # Create input fields and labels
    tk.Label(signup_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
    name_entry = tk.Entry(signup_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(signup_window, text="Surname:").grid(row=1, column=0, padx=10, pady=5)
    surname_entry = tk.Entry(signup_window)
    surname_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(signup_window, text="Email:").grid(row=2, column=0, padx=10, pady=5)
    email_entry = tk.Entry(signup_window)
    email_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(signup_window, text="Contact Number:").grid(row=3, column=0, padx=10, pady=5)
    contact_number_entry = tk.Entry(signup_window)
    contact_number_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(signup_window, text="Password:").grid(row=4, column=0, padx=10, pady=5)
    password_entry = tk.Entry(signup_window, show="*")  # Password masking
    password_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(signup_window, text="Confirm Password:").grid(row=5, column=0, padx=10, pady=5)
    confirm_password_entry = tk.Entry(signup_window, show="*")  # Password masking
    confirm_password_entry.grid(row=5, column=1, padx=10, pady=5)

    # Function to handle passenger registration
    def register_passenger():
        name = name_entry.get().strip()
        surname = surname_entry.get().strip()
        email = email_entry.get().strip()
        contact_number = contact_number_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()

        # Validate inputs
        if not name or not surname or not email or not contact_number or not password or not confirm_password:
            messagebox.showerror("Error", "All fields are required!")
            return

        if len(name) < 2:
            messagebox.showerror("Error", "Name must be at least 2 characters long!")
            return

        if len(surname) < 2:
            messagebox.showerror("Error", "Surname must be at least 2 characters long!")
            return

        if len(contact_number) < 10 or not contact_number.isdigit():
            messagebox.showerror("Error", "Contact number must be at least 10 digits and contain only numbers!")
            return

        # Validate password (must contain letters and digits)
        if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Error", "Password must contain both letters and numbers, and be at least 6 characters long!")
            return

        # Check if passwords match
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        # Connect to the database
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            try:
                # Check for duplicate email
                query_check = "SELECT email FROM User WHERE email=%s"
                cursor.execute(query_check, (email,))
                existing_record = cursor.fetchone()

                if existing_record:
                    messagebox.showerror("Error", "Email already exists!")
                    return

                # Insert new passenger into the database (User table used for login)
                query_insert_user = """
                    INSERT INTO User (username, name, surname, password, contact_number, role, email)
                    VALUES (%s, %s, %s, %s, %s, 'Passenger', %s)
                """
                # For now, using password directly (but it should be hashed)
                cursor.execute(query_insert_user, (name.lower(), name, surname, password, contact_number, email))
                connection.commit()
                messagebox.showinfo("Success", "Passenger registered successfully!")

                # Clear fields
                name_entry.delete(0, tk.END)
                surname_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                contact_number_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                confirm_password_entry.delete(0, tk.END)

                # Close the signup window
                signup_window.destroy()

            except mysql.connector.IntegrityError:
                messagebox.showerror("Integrity Error", "Duplicate entry detected!")
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
        else:
            messagebox.showerror("Database Error", "Could not connect to the database!")

    # Button to register passenger
    tk.Button(signup_window, text="Sign Up", font=("Arial", 14), command=register_passenger).grid(row=6, columnspan=2, pady=20)

    signup_window.mainloop()

def passenger_dashboard():
    # Create the passenger dashboard window
    passenger_window = tk.Toplevel()  # Use Toplevel instead of Tk to avoid blocking the main window
    passenger_window.title("Passenger Dashboard")

    # Set the window to full screen
    passenger_window.attributes("-fullscreen", True)

    # Set the background using Canvas
    try:
        # Load the background image (make sure to update the path)
        set_background(passenger_window, "assets/backgrounds/passenger_dash.jpg")
        img = img.resize((passenger_window.winfo_screenwidth(), passenger_window.winfo_screenheight()), Image.Resampling.LANCZOS)
        bg_img = ImageTk.PhotoImage(img)

        # Create a Canvas and set the image as background
        canvas = tk.Canvas(passenger_window, width=passenger_window.winfo_screenwidth(), height=passenger_window.winfo_screenheight())
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_img, anchor="nw")

        # Keep the background image in memory by attaching it to the window
        passenger_window.bg_img = bg_img

    except Exception as e:
        print(f"Error loading background image: {e}")
        passenger_window.configure(bg="white")  # Fallback to white background

    # Add buttons for passenger actions with similar positioning as in admin dashboard
    tk.Button(passenger_window, text="Search Flights", font=("Arial", 20), command=search_flights).place(relx=0.05, rely=0.1, anchor="w")
    tk.Button(passenger_window, text="View Booking Details", font=("Arial", 20), command=lambda: view_booking_details()).place(relx=0.05, rely=0.2, anchor="w")
    tk.Button(passenger_window, text="Cancel Booking", font=("Arial", 20), command=cancel_booking).place(relx=0.05, rely=0.3, anchor="w")
    tk.Button(passenger_window, text="Update Profile", font=("Arial", 20), command=update_profile).place(relx=0.05, rely=0.4, anchor="w")
    tk.Button(passenger_window, text="Download Ticket", font=("Arial", 20), command=download_ticket).place(relx=0.05, rely=0.5, anchor="w")
    tk.Button(passenger_window, text="Exit", font=("Arial", 20), command=passenger_window.destroy).place(relx=0.05, rely=0.9, anchor="w")

    # Start the Tkinter main loop to display the window
    passenger_window.mainloop()

def search_flights():
    search_window = tk.Toplevel()
    search_window.title("Search Flights")

    # Fetch airport data
    airports = fetch_airports()  # Ensure this function returns a list of airports in "Name - Code" format

    # Departure Airport Label and Combobox
    departure_label = tk.Label(search_window, text="Departure Airport:")
    departure_label.grid(row=0, column=0, padx=10, pady=10)
    departure_combo = ttk.Combobox(search_window, values=airports, state="readonly")
    departure_combo.grid(row=0, column=1, padx=10, pady=10)

    # Destination Airport Label and Combobox
    destination_label = tk.Label(search_window, text="Destination Airport:")
    destination_label.grid(row=1, column=0, padx=10, pady=10)
    destination_combo = ttk.Combobox(search_window, values=airports, state="readonly")
    destination_combo.grid(row=1, column=1, padx=10, pady=10)

    # Departure Date Label and Calendar Button
    date_label = tk.Label(search_window, text="Departure Date:")
    date_label.grid(row=2, column=0, padx=10, pady=10)
    date_entry = tk.Entry(search_window)
    date_entry.grid(row=2, column=1, padx=10, pady=10)

    def open_calendar():
        calendar_window = tk.Toplevel(search_window)
        calendar_window.title("Select Date")
        cal = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-MM-dd")
        cal.pack(pady=20)

        def select_date():
            date_entry.delete(0, tk.END)
            date_entry.insert(0, cal.get_date())
            calendar_window.destroy()

        select_button = tk.Button(calendar_window, text="Select", command=select_date)
        select_button.pack(pady=10)

    calendar_button = tk.Button(search_window, text="Open Calendar", command=open_calendar)
    calendar_button.grid(row=2, column=2, padx=10, pady=10)

    # Create Treeview widget for displaying flight results (initially empty)
    columns = ("flight_id", "departure_date", "departure_time", "arrival_date", "arrival_time", "status",
               "total_seats", "economy_price", "business_price", "price_last_updated")
    tree = ttk.Treeview(search_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=120)

    # Add scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(search_window, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=4, column=2, sticky="ns", pady=10)
    tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Search Function
    def search():
        departure = departure_combo.get().split(" - ")[0]  # Extract airport code
        destination = destination_combo.get().split(" - ")[0]  # Extract airport code
        date = date_entry.get()

        if not departure or not destination or not date:
            messagebox.showerror("Error", "All fields must be filled!")
            passenger_dashboard()
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            query = """
                SELECT flight_id, departure_date, departure_time, arrival_date, arrival_time, status, total_seats,
                       economy_price, business_price, price_last_updated
                FROM flight
                WHERE departure_airport = %s AND destination_airport = %s AND departure_date >= %s
            """

            cursor.execute(query, (departure, destination, date))
            results = cursor.fetchall()

            # Clear any previous results from the Treeview
            for item in tree.get_children():
                tree.delete(item)

            # Insert flight data into the Treeview
            for row in results:
                tree.insert("", tk.END, values=row)

            if not results:
                messagebox.showinfo("No Results", "No flights found matching the search criteria.")
                passenger_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Error fetching flights: {str(e)}")
            passenger_dashboard()
        finally:
            if conn:
                conn.close()

    search_button = tk.Button(search_window, text="Search Flights", command=search)
    search_button.grid(row=3, column=1, pady=20)

    # Define the book_seats function inside search_flights
    def book_seats():
        # Select flight from search results
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a flight to book seats.")
            return

        flight_id = tree.item(selected_item)["values"][0]  # Get flight_id of selected flight

        # Create a new booking window
        book_window = tk.Toplevel(search_window)
        book_window.title("Book Seats")

        # Connect to the database
        conn = connect_to_database()
        cursor = conn.cursor()

        # Fetch available seats for the selected flight
        cursor.execute("SELECT seat_number, is_available FROM seat WHERE flight_id = %s", (flight_id,))
        seats = cursor.fetchall()

        # Listbox to display available seats
        seat_listbox = tk.Listbox(book_window)
        for seat in seats:
            seat_status = "Available" if seat[1] else "Booked"
            seat_listbox.insert(tk.END, f"Seat {seat[0]} - {seat_status}")
        seat_listbox.pack()

        def book_seat():
            selected_seat_index = seat_listbox.curselection()
            if not selected_seat_index:
                messagebox.showerror("Error", "Please select a seat first.")
                return

            selected_seat = seat_listbox.get(selected_seat_index)
            seat_number = selected_seat.split()[1]

            # Check if the seat is available before booking
            cursor.execute("SELECT is_available FROM seat WHERE seat_number = %s AND flight_id = %s", (seat_number, flight_id))
            seat_status = cursor.fetchone()[0]
            if seat_status == 0:
                messagebox.showerror("Error", "This seat is already booked.")
                passenger_dashboard()
                return

            # Update seat status to "Booked" (0 means booked)
            cursor.execute("UPDATE seat SET is_available = 0 WHERE seat_number = %s AND flight_id = %s", (seat_number, flight_id))
            conn.commit()

            messagebox.showinfo("Success", "Seat booked successfully.")
            passenger_dashboard()

        # Book seat button
        book_button = tk.Button(book_window, text="Book Seat", command=book_seat)
        book_button.pack()

    # Add Book Seat button
    book_seat_button = tk.Button(search_window, text="Book Seat", command=book_seats)
    book_seat_button.grid(row=5, column=1, pady=20)

def view_booking_details():
    booking_window = tk.Toplevel()
    booking_window.title("View Booking Details")
    
    # Set a larger size for the window (width x height)
    booking_window.geometry("600x400+500+100")  # You can adjust these values as needed

    # Ask the passenger for their email
    email_label = tk.Label(booking_window, text="Enter your email:")
    email_label.pack(pady=10)

    email_entry = tk.Entry(booking_window)
    email_entry.pack(pady=10)

    def fetch_booking_details():
        email = email_entry.get()

        if not email:
            messagebox.showerror("Error", "Please enter your email.")
            passenger_dashboard()
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Get the user_id for the given email
            cursor.execute("SELECT user_id FROM User WHERE email=%s AND role='Passenger'", (email,))
            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Error", "No user found with that email.")
                passenger_dashboard()
                return

            user_id = user[0]

            # Now fetch the booking details for the user
            cursor.execute("""
                SELECT b.booking_id, f.flight_id, f.departure_airport, f.destination_airport, f.departure_date
                FROM Booking b
                JOIN Flight f ON b.flight_id = f.flight_id
                WHERE b.user_id = %s
            """, (user_id,))

            bookings = cursor.fetchall()

            if not bookings:
                messagebox.showinfo("No Bookings", "You have no bookings.")
                passenger_dashboard()

            for booking in bookings:
                booking_info = f"Booking {booking[0]} | Flight {booking[1]} | {booking[2]} to {booking[3]} | Departure: {booking[4]}"
                tk.Label(booking_window, text=booking_info).pack(pady=5)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            passenger_dashboard()
        finally:
            cursor.close()
            connection.close()

    # Button to trigger booking details fetch
    fetch_button = tk.Button(booking_window, text="Fetch Booking Details", command=fetch_booking_details)
    fetch_button.pack(pady=20)

def cancel_booking():
    cancel_window = tk.Toplevel()
    cancel_window.title("Cancel Booking")
    cancel_window.geometry("600x400+500+100")

    # Prompt the user for email
    email_label = tk.Label(cancel_window, text="Enter your email:")
    email_label.pack()

    email_entry = tk.Entry(cancel_window)
    email_entry.pack()

    def fetch_bookings():
        email = email_entry.get()

        if not email:
            messagebox.showerror("Error", "Please enter your email.")
            return

        try:
            connection = connect_to_database()
            cursor = connection.cursor()

            # Fetch the user_id based on the entered email
            cursor.execute("SELECT user_id FROM User WHERE email=%s AND role='Passenger'", (email,))
            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Error", "No user found with that email.")
                passenger_dashboard()
                return

            user_id = user[0]

            # Now fetch the user's bookings
            cursor.execute("""
                SELECT b.booking_id, f.flight_id, f.departure_airport, f.destination_airport, f.departure_date
                FROM Booking b
                JOIN Flight f ON b.flight_id = f.flight_id
                WHERE b.user_id = %s
            """, (user_id,))

            bookings = cursor.fetchall()

            if not bookings:
                messagebox.showinfo("No Bookings", "You have no bookings.")
                passenger_dashboard()
                return

            # Display the bookings in a Listbox
            booking_listbox.delete(0, tk.END)  # Clear the previous list
            for booking in bookings:
                booking_listbox.insert(tk.END, f"Booking {booking[0]} | Flight {booking[1]} | {booking[2]} to {booking[3]} | Departure: {booking[4]}")
            booking_listbox.pack()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            passenger_dashboard()
        finally:
            cursor.close()
            connection.close()

    def cancel():
        try:
            selected_booking = booking_listbox.get(booking_listbox.curselection()).split()[1]
            connection = connect_to_database()
            cursor = connection.cursor()

            # Delete the booking
            cursor.execute("DELETE FROM Booking WHERE booking_id = %s", (selected_booking,))
            connection.commit()

            messagebox.showinfo("Success", "Booking cancelled successfully.")
            passenger_dashboard()
            booking_listbox.delete(0, tk.END)  # Clear the list after cancellation

        except IndexError:
            messagebox.showerror("Error", "Please select a booking to cancel.")
            passenger_dashboard()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            passenger_dashboard()
        finally:
            cursor.close()
            connection.close()

    # Button to fetch bookings after entering email
    fetch_button = tk.Button(cancel_window, text="Fetch Bookings", command=fetch_bookings)
    fetch_button.pack()

    # Listbox to display bookings
    booking_listbox = tk.Listbox(cancel_window)
    booking_listbox.pack()

    # Button to cancel selected booking
    cancel_button = tk.Button(cancel_window, text="Cancel Booking", command=cancel)
    cancel_button.pack()

def update_profile():
    # Create the update window
    update_window = tk.Toplevel()
    update_window.title("Update Profile")
    update_window.geometry("600x400+500+100")

    # Step 1: Authenticate the user by email and password
    tk.Label(update_window, text="Enter your email:", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=10)
    email_entry = tk.Entry(update_window)
    email_entry.grid(row=0, column=1, pady=10, padx=10)

    tk.Label(update_window, text="Enter your password:", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=10)
    password_entry = tk.Entry(update_window, show="*")
    password_entry.grid(row=1, column=1, pady=10, padx=10)

    def authenticate_user():
        email = email_entry.get()
        password = password_entry.get()

        if not email or not password:
            tk.messagebox.showerror("Error", "Please enter both email and password.")
            return

        try:
            # Create a new database connection
            connection = connect_to_database()
            if not connection:
                tk.messagebox.showerror("Database Error", "Failed to connect to database")
                return
                
            cursor = connection.cursor()

            # Verify the email and password
            cursor.execute("SELECT user_id, password FROM User WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or user[1] != password:
                tk.messagebox.showerror("Authentication Error", "Invalid email or password.")
                cursor.close()
                connection.close()
                return

            user_id = user[0]

            # Step 2: Fetch current profile details for the authenticated user
            cursor.execute("SELECT contact_number FROM User WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()

            # Close the cursor and connection after fetching data
            cursor.close()
            connection.close()

            # Create labels and entry fields for new contact_number and password
            tk.Label(update_window, text="New Contact Number:", font=("Arial", 12)).grid(row=2, column=0, pady=10, padx=10)
            new_contact_entry = tk.Entry(update_window)
            new_contact_entry.insert(0, profile[0])
            new_contact_entry.grid(row=2, column=1, pady=10, padx=10)

            tk.Label(update_window, text="New Password:", font=("Arial", 12)).grid(row=3, column=0, pady=10, padx=10)
            new_password_entry = tk.Entry(update_window, show="*")
            new_password_entry.grid(row=3, column=1, pady=10, padx=10)

            tk.Label(update_window, text="Confirm New Password:", font=("Arial", 12)).grid(row=4, column=0, pady=10, padx=10)
            confirm_password_entry = tk.Entry(update_window, show="*")
            confirm_password_entry.grid(row=4, column=1, pady=10, padx=10)

            def update_profile_details():
                new_contact = new_contact_entry.get()
                new_password = new_password_entry.get()
                confirm_password = confirm_password_entry.get()

                if new_password != confirm_password:
                    tk.messagebox.showerror("Password Error", "Passwords do not match.")
                    return

                # Prepare SQL query to update the profile
                update_fields = []
                params = []

                if new_contact != profile[0]:
                    update_fields.append("contact_number = %s")
                    params.append(new_contact)

                if new_password:
                    update_fields.append("password = %s")
                    params.append(new_password)

                # Add user_id to parameters
                params.append(user_id)

                if update_fields:
                    try:
                        # Create a new connection for the update
                        update_connection = connect_to_database()
                        if not update_connection:
                            tk.messagebox.showerror("Database Error", "Failed to connect to database")
                            return
                            
                        update_cursor = update_connection.cursor()
                        
                        update_cursor.execute(f"""
                            UPDATE User
                            SET {', '.join(update_fields)}
                            WHERE user_id = %s
                        """, tuple(params))
                        update_connection.commit()
                        
                        update_cursor.close()
                        update_connection.close()
                        
                        tk.messagebox.showinfo("Success", "Profile updated successfully.")
                        update_window.destroy()
                    except mysql.connector.Error as e:
                        tk.messagebox.showerror("Database Error", f"Error: {e}")
                else:
                    tk.messagebox.showwarning("No Changes", "No changes made to profile.")

            # Button to save the updated profile
            update_button = tk.Button(update_window, text="Update Profile", command=update_profile_details)
            update_button.grid(row=5, column=0, columnspan=2, pady=20)

            # Button to exit the update window
            exit_button = tk.Button(update_window, text="Exit", command=update_window.destroy)
            exit_button.grid(row=6, column=0, columnspan=2, pady=10)

        except mysql.connector.Error as e:
            tk.messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            # Ensure connection is closed if it was created
            if 'connection' in locals() and connection:
                connection.close()

    # Button to authenticate user and load the profile details for editing
    authenticate_button = tk.Button(update_window, text="Authenticate", command=authenticate_user)
    authenticate_button.grid(row=5, column=0, columnspan=2, pady=20)


def download_ticket():
    ticket_window = tk.Toplevel()
    ticket_window.title("Download Ticket")

    user_id = 1  # Assuming the user is logged in
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.booking_id, f.flight_id, f.departure_airport, f.destination_airport, f.departure_date
        FROM bookings b
        JOIN flights f ON b.flight_id = f.flight_id
        WHERE b.user_id = ?
    """, (user_id,))
    tickets = cursor.fetchall()

    ticket_listbox = tk.Listbox(ticket_window)
    for ticket in tickets:
        ticket_listbox.insert(tk.END, f"Booking {ticket[0]} | Flight {ticket[1]} | {ticket[2]} to {ticket[3]}")
    ticket_listbox.pack()

    def download():
        selected_ticket = ticket_listbox.get(ticket_listbox.curselection())
        booking_id = selected_ticket.split()[1]

        # Generate PDF Ticket
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Booking ID: {booking_id}", ln=True)
        pdf.cell(200, 10, txt=f"Flight: {selected_ticket}", ln=True)

        pdf.output(f"ticket_{booking_id}.pdf")
        messagebox.showinfo("Success", "Ticket downloaded successfully.")
        passenger_dashboard()

    download_button = tk.Button(ticket_window, text="Download Ticket", command=download)
    download_button.pack()