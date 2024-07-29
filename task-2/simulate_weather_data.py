import sqlite3
import random
from datetime import datetime, timedelta

def generate_simulated_data(start_date, days, cities):
    conditions = ["Clear", "Cloudy", "Rain", "Snow", "Thunderstorm"]
    simulated_data = []

    for day in range(days):
        date = start_date + timedelta(days=day)
        dt_epoch = int(date.timestamp())
        for city in cities:
            # Generate random temperature and weather conditions
            temp = random.uniform(15.0, 35.0)  # Random temperature between 15°C and 35°C
            feels_like = temp + random.uniform(-2.0, 2.0)  # Feels like temperature
            condition = random.choice(conditions)
            
            # Calculate avg_temp, min_temp, and max_temp
            avg_temp = temp  # In a real scenario, you might compute these differently
            min_temp = temp - random.uniform(2.0, 5.0)  # Simulate minimum temperature
            max_temp = temp + random.uniform(2.0, 5.0)  # Simulate maximum temperature
            
            simulated_data.append((city, temp, feels_like, condition, dt_epoch, avg_temp, min_temp, max_temp))

    return simulated_data

def insert_simulated_data(conn, cursor, data):
    cursor.executemany('''
        INSERT INTO weather (city, temp, feels_like, main, dt, avg_temp, min_temp, max_temp) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()

def main():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()

    cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
    start_date = datetime.now() - timedelta(days=30)  # Simulate data for the last 30 days
    days = 30
    simulated_data = generate_simulated_data(start_date, days, cities)
    insert_simulated_data(conn, cursor, simulated_data)

    conn.close()

if __name__ == "__main__":
    main()
