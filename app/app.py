import sqlite3
from flask import Flask, request, jsonify
import db

app = Flask(__name__)

# --- API Endpoints ---

@app.route('/')
def index():
    """Simple home endpoint to confirm the server is running."""
    return "Weather Web Service with Locations is running! Try /weather or /locations"

@app.route('/weather', methods=['GET'])
def weather():
    """
    Retrieves all weather records from the database, including location details.
    Can be optionally filtered by a limit query parameter.
    """
    limit = request.args.get('limit', type=int)

    try:
        weather_data = db.get_all_weather_data(limit)
        return jsonify(weather_data), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/weather/<timestamp>', methods=['GET'])
def get_weather_by_timestamp(timestamp):
    """
    Retrieves a specific weather record by timestamp, including location details.
    """

    try:
        row = get_weather_by_timestamp(timestamp)

        if isinstance(row,dict):
            return jsonify(row), 200
        else:
            return jsonify({"message": f"No data found for timestamp: {timestamp}"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/weather', methods=['POST'])
def add_weather_data():
    """
    Adds a new weather record to the database.
    Expects JSON input with timestamp, temperature, humidity, wind_speed, wind_direction, and location_name.
    location_id is determined from location_name. If location_name does not exist, it will be created
    with null lat/long, or you can provide lat/long to ensure it's fully populated.
    Example JSON payload:
    {
        "timestamp": "2023-01-01 07:00:00",
        "temperature": 7.5,
        "humidity": 76.0,
        "wind_speed": 1.8,
        "wind_direction": 135.0,
        "location_name": "London",
        "location_latitude": 51.5074,
        "location_longitude": -0.1278
    }
    """
    new_data = request.get_json()

    if not new_data:
        return jsonify({"error": "Invalid JSON data provided."}), 400

    required_fields = ['timestamp', 'temperature', 'humidity', 'wind_speed', 'wind_direction', 'location_name']
    for field in required_fields:
        if field not in new_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        _ = float(new_data['temperature'])
        _ = float(new_data['humidity'])
        _ = float(new_data['wind_speed'])
        _ = float(new_data['wind_direction'])
    except ValueError:
        return "error: Temperature, humidity, wind speed, and wind direction must be numbers."

    try:
        message = db.add_weather_data(new_data)
        status_code = 404 if message.startswith("error:") else 201 
        return jsonify({"message": message}), status_code
    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"{e}"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"{e}"}), 500

@app.route('/locations', methods=['GET'])
def locations():
    """Retrieves all locations from the database."""
    try:
        locations_data = db.get_all_locations()
        return jsonify(locations_data), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/locations', methods=['POST'])
def add_location():
    """
    Adds a new location to the database.
    Expects JSON input with name, latitude, and longitude.
    Example JSON payload:
    {
        "name": "Tokyo",
        "latitude": 35.6895,
        "longitude": 139.6917
    }
    """
    new_location = request.get_json()

    if not new_location:
        return jsonify({"error": "Invalid JSON data provided."}), 400

    required_fields = ['name', 'latitude', 'longitude']
    for field in required_fields:
        if field not in new_location:
            return jsonify({"error": f"Missing required field: '{field}'"}), 400

    name = new_location['name']
    try:
        _ = float(new_location['latitude'])
        _ = float(new_location['longitude'])
    except ValueError:
        return jsonify({"error": "Latitude and longitude must be numbers."}), 400

    try:
        message = db.add_location(new_location)
        status_code = 404 if message.startswith("error:") else 201 
        return jsonify({"message": message}), status_code
    except sqlite3.IntegrityError as e:
        return jsonify({"error": f"Database integrity error: '{e}'"}), 409
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500


# --- Run the Flask App ---
if __name__ == '__main__':
    # Initialize DB schema
    db.init_db()
    # Load initial data from CSVs if tables are empty
    db.load_initial_data()
    # Run in debug mode for development (auto-reloads, provides debugger)
    app.run(debug=True)
