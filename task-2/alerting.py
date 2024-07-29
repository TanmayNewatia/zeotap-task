from config import ALERT_THRESHOLD

def check_alerts(cursor):
    cursor.execute('SELECT city, temp FROM weather WHERE temp > ?', (ALERT_THRESHOLD,))
    alerts = cursor.fetchall()

    # Remove duplicates by using a dictionary with (city, temp) as keys
    unique_alerts = {}
    for city, temp in alerts:
        if (city, temp) not in unique_alerts:
            unique_alerts[(city, temp)] = True

    if unique_alerts:
        print("Alerts:")
        for (city, temp) in unique_alerts.keys():
            print(f"Alert: {city} has exceeded the temperature threshold with {temp:.2f}°C")
    else:
        print("No alerts")
