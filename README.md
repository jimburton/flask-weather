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
$ git clone 
```

you must first populate the database by running the `main` method in
the class `loader.Main`. Do this in your ide or by running the maven target `mvn exec:java@loader`.

Now you can run the service by running the `main` method of the class `ci646.weather.Application`.
This starts the Spark application listening for HTTP requests at the address `http://localhost:4567`.
The webservice delivers JSON data via the following endpoints:

| Endpoint | Verb | Description |
| -------- | ---- | ----------- |
| `/locations` | `GET` | Retrieve an array of all locations |
| `/locations` | `POST` | Create a new location. `POST` data parameters expected are `name` (a string), `lat` (the latitude, floating point number), `lon` (the logitude, a floating point number), `asl` (a floating point number). The response will contain the new location. |
| `/locations/<loc>` | `GET` | Returns the location(s) matching `<loc>`. If `<loc>` is a number, the response will be the single location with this id, if one exists. If `<loc>` is a string, the response will be an array of location objects whose names fuzzily match that string. |
| `/records` | `GET` | Retrieve an array of all records. |
| `/records/<id>` | `GET` | Retrieve an array of all records with location id equal to `<id>`. |
| `/records/<id>/<from>/<to>` | `GET` | Retrieve an array of all records with location id equal to `<id>` and a timestamp that falls between `<from>` and `<to>`. These timestamps must be supplied in the format `yyyy-MM-ddTHH:mm`. For example `2020-12-01T00:00`. |
| `/records/<id>` | `POST` | Create a new record. `POST` data parameters expected are `ts` (a timestamp in the format given above), `temp` (the temperature, a floating point number), `hum` (the humidity, a floating point number), `ws` (the wind speed, a floating point number), `wd` (the wind direction, a floating point number). The response will contain the new record. |

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
