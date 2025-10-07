import mysql.connector as connector
from mysql.connector import Error
from config import DB_CONFIG

try:
    # Establishing connection to MySQL
    connection = connector.connect(**DB_CONFIG)
    
    cursor = connection.cursor()
    print("Connected to MySQL server.")
    
    cursor.execute("USE Airline_db")
    print("The database 'Airline_db' is set for use.")
    
    # Inserting realistic sample data into each table
    
    # airline table
    cursor.execute("""
        INSERT INTO airline (name, headquarters, founded_date, contact_number, hub_airport)
        VALUES
        ('SkyWings', 'New York', '1998-04-15', '2125550101', 'JFK'),
        ('CloudAir', 'London', '2002-06-10', '44-2075551234', 'LHR'),
        ('JetStream', 'Sydney', '2007-09-05', '6125559999', 'SYD'),
        ('PacificAir', 'Tokyo', '2011-11-20', '8135555678', 'HND'),
        ('GlobeAir', 'Paris', '2015-12-30', '33-1455552345', 'CDG');
    """)
    # airport table
    cursor.execute("""
        INSERT INTO airport (airport_code, name, city, country)
        VALUES
        ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
        ('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
        ('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
        ('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan'),
        ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France');
    """)

    # airplane table
    cursor.execute("""
        INSERT INTO airplane (registration_number, model_number, capacity, location, airline_id)
        VALUES
        ('AB123', 'Boeing 737', 180, 'New York', 1),
        ('CD456', 'Airbus A320', 160, 'London', 2),
        ('EF789', 'Boeing 787', 250, 'Sydney', 3),
        ('GH101', 'Airbus A380', 500, 'Tokyo', 4),
        ('IJ202', 'Boeing 777', 350, 'Paris', 5);
    """)

    # pilot table
    cursor.execute("""
        INSERT INTO pilot (name, address, contact_number, salary, medical_exam_date)
        VALUES
        ('John Doe', '123 Elm Street, New York', '2125551111', 80000, '2024-02-01'),
        ('Emma Smith', '456 Oak Avenue, London', '44-2075556789', 85000, '2024-03-01'),
        ('James Brown', '789 Pine Road, Sydney', '6125554321', 90000, '2024-04-01'),
        ('Olivia Johnson', '101 Maple Street, Tokyo', '8135552345', 95000, '2024-05-01'),
        ('Aiden Davis', '202 Birch Lane, Paris', '33-1455556789', 100000, '2024-06-01');
    """)

    # technician table
    cursor.execute("""
        INSERT INTO technician (name, address, contact_number, salary)
        VALUES
        ('Michael White', '500 Park Blvd, New York', '2125551234', 60000),
        ('Sophia Lee', '600 Cedar St, London', '44-2075559876', 65000),
        ('Daniel Green', '700 Oak Lane, Sydney', '6125556543', 70000),
        ('Isabella Clark', '800 Birch Ave, Tokyo', '8135556789', 75000),
        ('Lucas Harris', '900 Maple Rd, Paris', '33-1455551234', 80000);
    """)

    # operational_test table
    cursor.execute("""
        INSERT INTO operationaltest (test_name, min_value, test_date, status, airplane_id)
        VALUES
        ('Engine Performance', 85.5, '2024-01-10', 'Passed', 1),
        ('Landing Gear Check', 90.0, '2024-02-10', 'Passed', 2),
        ('Safety Systems', 95.0, '2024-03-15', 'Failed', 3),
        ('Fuel Efficiency', 80.0, '2024-04-01', 'Passed', 4),
        ('Wing Stress Test', 92.0, '2024-05-20', 'Passed', 5);
    """)

    # flight table
    cursor.execute("""
        INSERT INTO flight (departure_date, departure_time, arrival_date, arrival_time, status, total_seats, economy_price, business_price, price_last_updated, pilot_id, departure_airport, destination_airport, airplane_id)
        VALUES
        ('2024-01-15', '08:00:00', '2024-01-15', '12:00:00', 'On Time', 180, 150.00, 250.00, '2024-01-10', 1, 'JFK', 'LHR', 1),
        ('2024-02-20', '09:30:00', '2024-02-20', '13:30:00', 'On Time', 160, 130.00, 230.00, '2024-02-15', 2, 'LHR', 'SYD', 2),
        ('2024-03-25', '11:00:00', '2024-03-25', '15:00:00', 'Delayed', 250, 200.00, 350.00, '2024-03-20', 3, 'SYD', 'HND', 3),
        ('2024-04-10', '14:00:00', '2024-04-10', '18:00:00', 'On Time', 500, 250.00, 400.00, '2024-04-01', 4, 'HND', 'CDG', 4),
        ('2024-05-05', '16:00:00', '2024-05-05', '20:00:00', 'Cancelled', 350, 180.00, 300.00, '2024-05-01', 5, 'CDG', 'JFK', 5);
    """)

    # user table (ensure admin)
    cursor.execute("""
        INSERT INTO user (username, name, surname, password, contact_number, role, email)
        VALUES
        ('admin', 'Admin', 'User', 'admin123', '2125550001', 'Admin', 'admin@example.com'),
        ('passenger1', 'John', 'Doe', 'john123', '2125551111', 'Passenger', 'john.doe@example.com'),
        ('passenger2', 'Emma', 'Smith', 'emma123', '44-2075556789', 'Passenger', 'emma.smith@example.com'),
        ('passenger3', 'James', 'Brown', 'james123', '6125554321', 'Passenger', 'james.brown@example.com'),
        ('passenger4', 'Olivia', 'Johnson', 'olivia123', '8135552345', 'Passenger', 'olivia.johnson@example.com');
    """)

    # booking table
    cursor.execute("""
        INSERT INTO booking (booking_date, luggage_weight, flight_id, user_id)
        VALUES
        ('2024-01-01', 20.5, 1, 2),
        ('2024-02-10', 15.0, 2, 3),
        ('2024-03-15', 18.0, 3, 4),
        ('2024-04-01', 22.0, 4, 5),
        ('2024-05-01', 10.0, 5, 1);
    """)

    # seat table
    cursor.execute("""
        INSERT INTO seat (seat_number, is_available, flight_id)
        VALUES
        ('A1', TRUE, 1),
        ('A2', TRUE, 1),
        ('A3', FALSE, 2),
        ('B1', TRUE, 3),
        ('B2', FALSE, 4);
    """)

    # ticket table
    cursor.execute("""
        INSERT INTO ticket (ticket_price, booking_status, issued_date, seat_id, flight_id, booking_id)
        VALUES
        (150.00, 'Confirmed', '2024-01-01', 1, 1, 1),
        (130.00, 'Confirmed', '2024-02-10', 2, 2, 2),
        (200.00, 'Cancelled', '2024-03-15', 3, 3, 3),
        (250.00, 'Confirmed', '2024-04-01', 4, 4, 4),
        (180.00, 'Pending', '2024-05-01', 5, 5, 5);
    """)

    # payment table
    cursor.execute("""
        INSERT INTO payment (payment_date, payment_method, booking_id)
        VALUES
        ('2024-01-01', 'Credit Card', 1),
        ('2024-02-10', 'Debit Card', 2),
        ('2024-03-15', 'PayPal', 3),
        ('2024-04-01', 'Credit Card', 4),
        ('2024-05-01', 'Cash', 5);
    """)

    # crewmember table
    cursor.execute("""
        INSERT INTO crewmember (name, role, flight_id, contact_number)
        VALUES
        ('William Clark', 'Flight Attendant', 1, '2125550102'),
        ('Sophia Harris', 'Pilot', 2, '44-2075552345'),
        ('Daniel King', 'Engineer', 3, '6125556789'),
        ('Emily Wright', 'Flight Attendant', 4, '8135555678'),
        ('Alexander Scott', 'Pilot', 5, '33-1455553456');
    """)

    connection.commit()

    print("Data inserted successfully into all tables.")
    
except Error as e:
    print("Error while connecting to MySQL or inserting data:", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection closed.")
