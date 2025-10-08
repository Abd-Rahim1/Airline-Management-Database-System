from database import connect_to_database
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk

def set_background(window, image_path):
    try:
        # Resolve absolute path
        bg_image_path = os.path.abspath(image_path)

        # Load and resize the image
        background_image = Image.open(bg_image_path)
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        background_image = background_image.resize((screen_width, screen_height))
        background_image = ImageTk.PhotoImage(background_image)

        # Create a canvas and place the background image
        canvas = tk.Canvas(window, width=screen_width, height=screen_height)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=background_image)
        canvas.image = background_image  # Keep a reference!

        return canvas

    except Exception as e:
        print(f" Error setting background: {e}")
        return None



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

def fetch_airplanes():
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT airplane_id, model_number FROM Airplane")
            airplanes = cursor.fetchall()
            return [f"{airplane_id} - {model_number}" for airplane_id, model_number in airplanes]
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching airplanes: {str(e)}")
    finally:
        if conn:
            conn.close()
    return []

def fetch_pilots():
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT pilot_id, name FROM Pilot")
            pilots = cursor.fetchall()
            return [f"{pilot_id} - {name}" for pilot_id, name in pilots]
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching pilots: {str(e)}")
    finally:
        if conn:
            conn.close()
    return []

def fetch_airports():
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT airport_code, city FROM Airport")
            airports = cursor.fetchall()
            return [f"{airport_code} - {city}" for airport_code, city in airports]
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching airports: {str(e)}")
    finally:
        if conn:
            conn.close()
    return []

def validate_date(date_string):
    try:
        from datetime import datetime
        datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validate_time(time_string):
    import re
    time_pattern = r"^(?:[01]?\d|2[0-3]):([0-5]?\d)$"
    return re.match(time_pattern, time_string) is not None

def clear_date_if_empty(event, field_var):
        """
        This function checks if the field's value is empty. 
        If empty, it resets the associated StringVar to an empty string.
        """
        if event.widget.get() == "":
            field_var.set("")