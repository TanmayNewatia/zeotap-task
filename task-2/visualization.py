import matplotlib.pyplot as plt
import sqlite3

def plot_weather_summary(cursor):
    cursor.execute('SELECT city, AVG(temp) FROM weather GROUP BY city')
    data = cursor.fetchall()
    
    if not data:
        print("No data to visualize.")
        return

    cities, avg_temps = zip(*data)
    
    plt.figure(figsize=(10, 6))
    plt.bar(cities, avg_temps, color='skyblue')
    plt.xlabel('City')
    plt.ylabel('Average Temperature (°C)')
    plt.title('Average Temperature by City')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()  # Show plot and block script until plot window is closed

# Example usage
if __name__ == "__main__":
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    plot_weather_summary(cursor)
    conn.close()
