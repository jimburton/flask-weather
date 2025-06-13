# Simple webservice for weather data 

This repository contains a Flask applications implementing a webservice relating to weather data.

The webservice provides a REST API in front of an SQLite database
containing records of weather observations. Each observation contains the
following data:

+ a unique record id,
+ a location id,
+ the time at which the recording was made,
+ the temperature,
+ the humidity,
+ the wind speed, and
+ the wind direction.

Each location consists of the following data:

+ a unique location id,
+ its name, and
+ its latitude and longitude.

Run the service:

```bash
$ git clone https://github.com/jimburton/flask-weather.git
$ cd flask-weather
$ python app/app.py
```


The webservice delivers JSON data via the following endpoints:

| Endpoint | Verb | Description |
| -------- | ---- | ----------- |
| `/` | `GET` | Retrieve a welcome message. |
| `/weather` | `GET` | Retrieve all weather records from the database, including location details. Can be optionally filtered by a `limit` query parameter. |
| `/weather` | `POST` | Adds a new weather record to the database. Expects JSON input with `timestamp`, `temperature`, `humidity`, `wind_speed`, `wind_direction`, and `location_name`. `location_id` is determined from `location_name`. If `location_name` does not exist, it will be created with null lat/long, or you can provide lat/long to ensure it's fully populated. |
| `/weather/<timestamp>` | `GET` | Retrieves a specific weather record by timestamp, including location details. |
| `/locations` | `GET` | Retrieve all locations. |
| `/locations` | `POST` | Adds a new location to the database. Expects JSON input with `name`, `latitude`, and `longitude`. |

## Testing the endpoints

You can use the UNIX command line tool `curl` to call these endpoints with the right kinds of request. For example,

GET all locations:

```
curl http://127.0.0.1:5000/locations
```

POST a new location:

```
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "Berlin",
    "latitude": 52.5200,
    "longitude": 13.4050
}' http://127.0.0.1:5000/locations
```

POST new weather data (referencing a location by name):

```
curl -X POST -H "Content-Type: application/json" -d '{
    "timestamp": "2023-01-01 08:00:00",
    "temperature": 6.8,
    "humidity": 78.2,
    "wind_speed": 2.1,
    "wind_direction": 150.0,
    "location_name": "Berlin"
}' http://127.0.0.1:5000/weather
```
