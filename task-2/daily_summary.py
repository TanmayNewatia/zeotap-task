import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

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
        # Ensure lists are not empty
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

def plot_weather_summary(cursor):
    # Calculate daily summaries
    summaries = calculate_daily_summary(cursor)
    # Plot the daily summaries
    plot_daily_summaries(summaries)
