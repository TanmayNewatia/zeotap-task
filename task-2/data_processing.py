import requests
from config import API_KEY, BASE_URL, COORDINATES
import sqlite3
from datetime import datetime, timedelta

def fetch_weather_data(lat, lon, api_key):
    url = f"{BASE_URL}?key={api_key}&q={lat},{lon}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error fetching data: {data.get('error', {}).get('message', 'Unknown error')}")
        return None
    
    return data

def store_weather_data(conn, cursor, city, temp, feels_like, condition, dt, avg_temp=None, min_temp=None, max_temp=None):
    cursor.execute('''
    INSERT INTO weather (city, temp, feels_like, main, dt, avg_temp, min_temp, max_temp) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (city, temp, feels_like, condition, dt, avg_temp, min_temp, max_temp))
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
        
        # Example of calculating or assigning avg_temp, min_temp, max_temp
        avg_temp = temp  # In a real scenario, this might be calculated differently
        min_temp = temp - 5  # Example value, replace with actual logic if needed
        max_temp = temp + 5  # Example value, replace with actual logic if needed
        
        store_weather_data(conn, cursor, city, temp, feels_like, condition, dt, avg_temp, min_temp, max_temp)
