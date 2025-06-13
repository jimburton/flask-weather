import csv
import sqlite3
import os

# --- Configuration ---
DATABASE_NAME = 'data/weather_data.db'
LOCATIONS_TABLE_NAME = 'locations'
MEASUREMENTS_TABLE_NAME = 'measurements'
LOCATIONS_CSV_FILE = 'data/locations.csv'
WEATHER_CSV_FILE = 'data/weather_data.csv'

# --- Database Helper Functions ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Enable foreign key support (important for SQLite)
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """Initializes the database schema (creates tables if they don't exist)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create locations table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {LOCATIONS_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            latitude REAL,
            longitude REAL
        )
    ''')

    # Create measurements table with foreign key to locations
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {MEASUREMENTS_TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL UNIQUE,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            wind_direction REAL,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES {LOCATIONS_TABLE_NAME} (id)
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' and tables '{LOCATIONS_TABLE_NAME}', '{MEASUREMENTS_TABLE_NAME}' created.")

def get_or_create_location_id(conn, name, latitude, longitude):
    """
    Retrieves location_id for a given name, creating the location if it doesn't exist.
    Returns the location_id.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {LOCATIONS_TABLE_NAME} WHERE name = ?", (name,))
    location = cursor.fetchone()

    if location:
        return location['id']
    else:
        cursor.execute(f'''
            INSERT INTO {LOCATIONS_TABLE_NAME} (name, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (name, latitude, longitude))
        conn.commit()
        print(f"Added new location: {name}")
        return cursor.lastrowid

def load_initial_data():
    """
    Loads data from CSV files into the database if tables are empty.
    This helps ensure data is present for testing.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if locations table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {LOCATIONS_TABLE_NAME}")
    locations_count = cursor.fetchone()[0]

    # Check if measurements table is empty
    cursor.execute(f"SELECT COUNT(*) FROM {MEASUREMENTS_TABLE_NAME}")
    measurements_count = cursor.fetchone()[0]

    if locations_count == 0 or measurements_count == 0:
        print("\nTables are empty. Attempting to load initial data from CSVs...")

        # Load locations data
        if os.path.exists(LOCATIONS_CSV_FILE):
            try:
                with open(LOCATIONS_CSV_FILE, 'r', newline='') as f:
                    reader = csv.reader(f)
                    header = next(reader) # Skip header
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            name = row[0]
                            latitude = float(row[1]) if row[1] else None
                            longitude = float(row[2]) if row[2] else None
                            get_or_create_location_id(conn, name, latitude, longitude) # This will insert or just get ID
                        except (ValueError, IndexError) as e:
                            print(f"Skipping locations.csv row {row_num} due to error: {row} - {e}")
                conn.commit()
                print(f"Loaded data from {LOCATIONS_CSV_FILE}")
            except Exception as e:
                print(f"Error loading {LOCATIONS_CSV_FILE}: {e}")
        else:
            print(f"Warning: {LOCATIONS_CSV_FILE} not found. Cannot load initial locations.")

        # Load weather data
        if os.path.exists(WEATHER_CSV_FILE):
            try:
                with open(WEATHER_CSV_FILE, 'r', newline='') as f:
                    reader = csv.reader(f)
                    header = next(reader) # Skip header
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            timestamp = row[0]
                            temperature = float(row[1]) if row[1] else None
                            humidity = float(row[2]) if row[2] else None
                            wind_speed = float(row[3]) if row[3] else None
                            wind_direction = float(row[4]) if row[4] else None
                            location_name = row[5]

                            location_id = get_or_create_location_id(conn, location_name, None, None) # Lat/Long can be None if already exists

                            cursor.execute(f'''
                                INSERT OR IGNORE INTO {MEASUREMENTS_TABLE_NAME} (timestamp, temperature, humidity, wind_speed, wind_direction, location_id)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (timestamp, temperature, humidity, wind_speed, wind_direction, location_id))
                        except (ValueError, IndexError) as e:
                            print(f"Skipping weather_data.csv row {row_num} due to error: {row} - {e}")
                conn.commit()
                print(f"Loaded data from {WEATHER_CSV_FILE}")
            except Exception as e:
                print(f"Error loading {WEATHER_CSV_FILE}: {e}")
        else:
            print(f"Warning: {WEATHER_CSV_FILE} not found. Cannot load initial weather data.")
    else:
        print("\nDatabase tables already contain data. Skipping initial CSV loading.")
    conn.close()

def get_all_weather_data(limit: int=None):
    """
    Retrieves all weather records from the database, including location details.
    Can be optionally filtered by a limit query parameter.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Join measurements with locations to get location name, lat, long
        query = f"""
            SELECT
                m.id, m.timestamp, m.temperature, m.humidity, m.wind_speed, m.wind_direction,
                l.name AS location_name, l.latitude AS location_latitude, l.longitude AS location_longitude
            FROM {MEASUREMENTS_TABLE_NAME} m
            LEFT JOIN {LOCATIONS_TABLE_NAME} l ON m.location_id = l.id
            ORDER BY m.timestamp DESC
        """
        if limit:
            cursor.execute(f"{query} LIMIT ?", (limit,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        weather_data = [dict(row) for row in rows]
        return weather_data
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()

def get_weather_by_timestamp(timestamp):
    """
    Retrieves a specific weather record by timestamp, including location details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"""
            SELECT
                m.id, m.timestamp, m.temperature, m.humidity, m.wind_speed, m.wind_direction,
                l.name AS location_name, l.latitude AS location_latitude, l.longitude AS location_longitude
            FROM {MEASUREMENTS_TABLE_NAME} m
            LEFT JOIN {LOCATIONS_TABLE_NAME} l ON m.location_id = l.id
            WHERE m.timestamp = ?
        """
        cursor.execute(query, (timestamp,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            return f"No data found for timestamp: {timestamp}"
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()

def add_weather_data(data:dict):
    """
    Adds a new weather record to the database.
    """

    timestamp = data['timestamp']
    location_name = data['location_name']
    location_latitude = data.get('location_latitude') # Optional for new location
    location_longitude = data.get('location_longitude') # Optional for new location
    temperature = float(data['temperature'])
    humidity = float(data['humidity'])
    wind_speed = float(data['wind_speed'])
    wind_direction = float(data['wind_direction'])

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get or create location and its ID
        location_id = get_or_create_location_id(conn, location_name, location_latitude, location_longitude)

        cursor.execute(f'''
            INSERT INTO {MEASUREMENTS_TABLE_NAME} (timestamp, temperature, humidity, wind_speed, wind_direction, location_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, temperature, humidity, wind_speed, wind_direction, location_id))
        conn.commit()
        return f"Weather data added successfully, id: {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        return f"error Data for timestamp '{timestamp}' already exists or invalid data: {e}"
    except sqlite3.Error as e:
        return f"error Database error: {e}"
    finally:
        conn.close()

def get_all_locations():
    """Retrieves all locations from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {LOCATIONS_TABLE_NAME} ORDER BY name")
        rows = cursor.fetchall()
        locations_data = [dict(row) for row in rows]
        return locations_data
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()

def add_location(data:dict):
    """
    Adds a new location to the database.
    """
    name = data['name']
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f'''
            INSERT INTO {LOCATIONS_TABLE_NAME} (name, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (name, latitude, longitude))
        conn.commit()
        return f"Location added successfully, id: {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        return f"error: Location with name '{name}' already exists."
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()
