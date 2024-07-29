# Weather Monitoring System Documentation

## Overview

The Weather Monitoring System is a real-time data processing application designed to monitor weather conditions and provide summarized insights. The system continuously fetches weather data from an external API, processes it, stores it in a local database, and generates visual summaries and alerts based on user-defined thresholds.

### Components

1. **Data Fetching**: Retrieves weather data from the OpenWeatherMap API.
2. **Database Management**: Stores weather data in an SQLite database.
3. **Data Processing**: Calculates daily summaries and checks for alert conditions.
4. **Visualization**: Generates plots for weather summaries.
5. **Alerts**: Notifies if certain weather conditions exceed predefined thresholds.

## Project Structure

- **`config.py`**: Contains configuration settings, including API keys and thresholds.
- **`db_setup.py`**: Sets up the SQLite database and defines schema.
- **`data_processing.py`**: Contains functions for fetching and storing weather data.
- **`alerting.py`**: Manages alerting logic based on thresholds.
- **`daily_summary.py`**: Calculates daily weather summaries and generates plots.
- **`main.py`**: Main script that integrates all components and runs the application.
- **`test_daily_summary.py`**: Unit tests for daily summary calculations.

## Configuration

### `config.py`

Contains configuration settings:

- `API_KEY`: API key for accessing weather data from OpenWeatherMap.
- `BASE_URL`: Base URL for API requests.
- `COORDINATES`: List of city coordinates for data fetching.
- `ALERT_THRESHOLD`: Temperature threshold for triggering alerts.
- `INTERVAL`: Interval for data fetching and processing (in seconds).

```python
API_KEY = 'your_api_key_here'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
COORDINATES = [
    ('Delhi', 28.6139, 77.2090),
    ('Mumbai', 19.0760, 72.8777),
    ('Chennai', 13.0827, 80.2707),
    ('Bangalore', 12.9716, 77.5946),
    ('Kolkata', 22.5726, 88.3639),
    ('Hyderabad', 17.3850, 78.4867)
]
ALERT_THRESHOLD = 35.0  # Temperature threshold for alerts
INTERVAL = 300  # Data fetching interval in seconds
```

## Database Setup

### `db_setup.py`

Sets up the SQLite database and schema:

```python
import sqlite3

def setup_database():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        temp REAL NOT NULL,
        feels_like REAL NOT NULL,
        main TEXT NOT NULL,
        dt INTEGER NOT NULL,
        avg_temp REAL,
        max_temp REAL,
        min_temp REAL
    )
    ''')
    
    conn.commit()
    print("Database Created Successfully")
    return conn, cursor

if __name__ == "__main__":
    setup_database()
```

## Data Processing

### `data_processing.py`

Fetches weather data from the API and stores it in the database:

```python
import requests
from config import API_KEY, BASE_URL, COORDINATES
import sqlite3
from datetime import datetime

def fetch_weather_data(lat, lon, api_key):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error fetching data: {data.get('error', {}).get('message', 'Unknown error')}")
        return None
    
    return data

def store_weather_data(conn, cursor, city, temp, feels_like, condition, dt):
    cursor.execute('INSERT INTO weather (city, temp, feels_like, main, dt) VALUES (?, ?, ?, ?, ?)',
                   (city, temp, feels_like, condition, dt))
    conn.commit()

def process_weather_data(conn, cursor):
    for city, lat, lon in COORDINATES:
        data = fetch_weather_data(lat, lon, API_KEY)
        
        if data is None or 'current' not in data:
            print(f"Invalid data received for {city}. Skipping.")
            continue
        
        current = data['current']
        temp = current['temp_c']
        feels_like = current['feelslike_c']
        condition = current['condition']['text']
        dt = current['last_updated_epoch']
        store_weather_data(conn, cursor, city, temp, feels_like, condition, dt)
```

## Alerting

### `alerting.py`

Checks if the temperature exceeds the predefined threshold and generates alerts:

```python
from config import ALERT_THRESHOLD

def check_alerts(cursor):
    cursor.execute('SELECT city, temp FROM weather WHERE temp > ?', (ALERT_THRESHOLD,))
    alerts = cursor.fetchall()

    # Remove duplicates
    unique_alerts = list(set(alerts))

    if unique_alerts:
        print("Alerts:")
        for city, temp in unique_alerts:
            print(f"Alert: {city} has exceeded the temperature threshold with {temp:.2f}°C")
    else:
        print("No alerts")
```

## Daily Summary and Visualization

### `daily_summary.py`

Calculates daily weather summaries and plots them:

```python
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime

def calculate_daily_summary(cursor):
    cursor.execute('''
        SELECT city, strftime('%Y-%m-%d', datetime(dt, 'unixepoch')) as date,
               AVG(temp) as avg_temp,
               MAX(temp) as max_temp,
               MIN(temp) as min_temp
        FROM weather
        GROUP BY city, date
    ''')
    
    data = cursor.fetchall()
    
    summaries = {}
    for city, date, avg_temp, max_temp, min_temp in data:
        if city not in summaries:
            summaries[city] = {'dates': [], 'avg_temps': [], 'max_temps': [], 'min_temps': []}
        summaries[city]['dates'].append(date)
        summaries[city]['avg_temps'].append(avg_temp)
        summaries[city]['max_temps'].append(max_temp)
        summaries[city]['min_temps'].append(min_temp)

    return summaries

def plot_daily_summaries(summaries):
    for city, values in summaries.items():
        dates = values['dates']
        avg_temps = values['avg_temps']
        max_temps = values['max_temps']
        min_temps = values['min_temps']

        if not dates or not avg_temps or not max_temps or not min_temps:
            print(f"No data to plot for {city}.")
            continue
        
        plt.figure(figsize=(12, 6))
        
        plt.plot(dates, avg_temps, label='Average Temperature', marker='o')
        plt.plot(dates, max_temps, label='Max Temperature', marker='o')
        plt.plot(dates, min_temps, label='Min Temperature', marker='o')
        
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Daily Weather Summary for {city}')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.grid(True)
        plt.show()
```

## Main Application

### `main.py`

Integrates all components and runs the application:

```python
import time
from db_setup import setup_database
from data_processing import process_weather_data
from alerting import check_alerts
from daily_summary import calculate_daily_summary, plot_daily_summaries
from config import INTERVAL

def main():
    conn, cursor = setup_database()
    
    while True:
        process_weather_data(conn, cursor)
        check_alerts(cursor)
        
        # Calculate and plot daily summaries
        summaries = calculate_daily_summary(cursor)
        plot_daily_summaries(summaries)
        
        # Pause execution for the specified interval
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
```

## Testing

### `test_daily_summary.py`

Contains unit tests for daily summary calculations:

```python
import unittest
import sqlite3
from daily_summary import calculate_daily_summary

class TestDailySummary(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect('weather_data.db')
        self.cursor = self.conn.cursor()
        self._setup_data()

    def _setup_data(self):
        # Insert test data for a single day
        self.cursor.execute('DELETE FROM weather')
        test_data = [
            ('Delhi', 30, 32, 'Clear', 1672531200),  # 2023-01-01
            ('Delhi', 28, 29, 'Clear', 1672534800),  # 2023-01-01
            ('Mumbai', 31, 33, 'Cloudy', 1672531200),  # 2023-01-01
        ]
        self.cursor.executemany('INSERT INTO weather (city, temp, feels_like, main, dt) VALUES (?, ?, ?, ?, ?)', test_data)
        self.conn.commit()

    def test_daily_summary(self):
        summaries = calculate_daily_summary(self.cursor)
        self.assertIn('Delhi', summaries)
        self.assertIn('Mumbai', summaries)
        self.assertEqual(len(summaries['Delhi']['dates']), 1)
        self.assertEqual(len(summaries['Mumbai']['dates']),

 1)
        self.assertAlmostEqual(summaries['Delhi']['avg_temps'][0], 29)
        self.assertEqual(summaries['Delhi']['max_temps'][0], 30)
        self.assertEqual(summaries['Delhi']['min_temps'][0], 28)

    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
```

## How to Run

1. **Set up the database**: Run `db_setup.py` to initialize the database schema.
2. **Fetch and store data**: Execute `main.py` to start the weather monitoring and processing loop.
3. **View results**: Check the generated plots and alerts as specified in the `main.py` script.
4. **Run tests**: Execute `test_daily_summary.py` to run unit tests and validate functionality.
