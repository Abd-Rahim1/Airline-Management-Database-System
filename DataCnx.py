import mysql.connector as connector
from mysql.connector import Error
from config import DB_CONFIG


try:
    # Establishing connection to MySQL
    connection = connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    print("Connected to MySQL server.")
    
    # Creating or switching to the desired database
    cursor.execute("CREATE DATABASE IF NOT EXISTS Airline_db")
    print("The database 'Airline_db' is created or already exists.")
    
    cursor.execute("USE Airline_db")
    print("The database 'Airline_db' is set for use.")
    
    # Create tables in correct order to avoid foreign key reference issues

    cursor.execute("""
        -- Table for Airline
        CREATE TABLE IF NOT EXISTS Airline (
            airline_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            headquarters VARCHAR(200),
            founded_date DATE,
            contact_number VARCHAR(15),
            hub_airport VARCHAR(10)
        );
    """)

    cursor.execute("""
        -- Table for Airport
        CREATE TABLE IF NOT EXISTS Airport (
            airport_code VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100),
            city VARCHAR(100),
            country VARCHAR(100)
        );
    """)

    cursor.execute("""
        -- Table for Airplane
        CREATE TABLE IF NOT EXISTS Airplane (
            airplane_id INT AUTO_INCREMENT PRIMARY KEY,
            registration_number VARCHAR(50) UNIQUE,
            model_number VARCHAR(50),
            capacity INT,
            location VARCHAR(100),
            airline_id INT,
            FOREIGN KEY (airline_id) REFERENCES Airline(airline_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for Pilot
        CREATE TABLE IF NOT EXISTS Pilot (
            pilot_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            address VARCHAR(200),
            contact_number VARCHAR(15),
            salary DECIMAL(10,2),
            medical_exam_date DATE
        );
    """)

    cursor.execute("""
        -- Table for Technician
        CREATE TABLE IF NOT EXISTS Technician (
            technician_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            address VARCHAR(200),
            contact_number VARCHAR(15),
            salary DECIMAL(10,2)
        );
    """)

    cursor.execute("""
        -- Table for OperationalTest
        CREATE TABLE IF NOT EXISTS OperationalTest (
            test_id INT AUTO_INCREMENT PRIMARY KEY,
            test_name VARCHAR(100),
            min_value DECIMAL(10,2),
            test_date DATE,
            status VARCHAR(50),
            airplane_id INT,
            FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for TechnicianAirplane
        CREATE TABLE IF NOT EXISTS TechnicianAirplane (
            technician_airplane_id INT AUTO_INCREMENT PRIMARY KEY,
            expertise VARCHAR(100),
            start_date DATE,
            end_date DATE,
            technician_id INT,
            airplane_id INT,
            FOREIGN KEY (technician_id) REFERENCES Technician(technician_id) ON DELETE CASCADE,
            FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for Flight
        CREATE TABLE IF NOT EXISTS Flight (
            flight_id INT AUTO_INCREMENT PRIMARY KEY,
            departure_date DATETIME,
            departure_time TIME,
            arrival_date DATETIME,
            arrival_time TIME,
            status VARCHAR(50),
            total_seats INT,
            economy_price DECIMAL,
            business_price DECIMAL,
            price_last_updated DATE,
            pilot_id INT,
            departure_airport VARCHAR(10),
            destination_airport VARCHAR(10),
            airplane_id INT,
            FOREIGN KEY (pilot_id) REFERENCES Pilot(pilot_id) ON DELETE SET NULL,
            FOREIGN KEY (departure_airport) REFERENCES Airport(airport_code) ON DELETE CASCADE,
            FOREIGN KEY (destination_airport) REFERENCES Airport(airport_code) ON DELETE CASCADE,
            FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for User (Admin and Passenger)
        CREATE TABLE IF NOT EXISTS User (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            name VARCHAR(100),
            surname VARCHAR(100),
            password VARCHAR(255),
            contact_number VARCHAR(255),
            role ENUM('Admin', 'Passenger'),
            email VARCHAR(255) UNIQUE
        );
    """)

    cursor.execute("""
        -- Table for Booking
        CREATE TABLE IF NOT EXISTS Booking (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_date DATETIME,
            luggage_weight DECIMAL,
            flight_id INT,
            user_id INT,
            FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for Seat
        CREATE TABLE IF NOT EXISTS Seat (
            seat_id INT AUTO_INCREMENT PRIMARY KEY,
            seat_number VARCHAR(10),
            is_available BOOLEAN,
            flight_id INT,
            FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for Ticket
        CREATE TABLE IF NOT EXISTS Ticket (
            ticket_id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_price DECIMAL(10,2),
            booking_status VARCHAR(50),
            issued_date DATE,
            seat_id INT,
            flight_id INT,
            booking_id INT,
            FOREIGN KEY (seat_id) REFERENCES Seat(seat_id) ON DELETE CASCADE,
            FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for Payment
        CREATE TABLE IF NOT EXISTS Payment (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            payment_date DATE,
            payment_method VARCHAR(50),
            booking_id INT,
            FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for CrewMember
        CREATE TABLE IF NOT EXISTS CrewMember (
            crew_member_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            role VARCHAR(50),
            flight_id INT,
            contact_number VARCHAR(15),
            FOREIGN KEY (flight_id) REFERENCES Flight(flight_id) ON DELETE CASCADE
        );
    """)

    cursor.execute("""
        -- Table for MaintenanceLog
        CREATE TABLE IF NOT EXISTS MaintenanceLog (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            maintenance_date DATE,
            description VARCHAR(100),
            technician_id INT,
            airplane_id INT,
            FOREIGN KEY (technician_id) REFERENCES Technician(technician_id) ON DELETE CASCADE,
            FOREIGN KEY (airplane_id) REFERENCES Airplane(airplane_id) ON DELETE CASCADE
        );
    """)

    print("All tables have been created successfully.")
    
    # Now, query the tables
    cursor.execute("SHOW TABLES")
    
    # Fetch and display the result of the query
    tables = cursor.fetchall()
    print("Total number of tables created:", len(tables))
    print("Table names:")
    for table in tables:
        print(table[0])

except connector.Error as err:
    print(f"Error: {err}")

finally:
    # Closing cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
