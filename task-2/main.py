import time
from db_setup import setup_database
from data_processing import process_weather_data
from alerting import check_alerts
from daily_summary import calculate_daily_summary, plot_daily_summaries
from config import INTERVAL

def main():
    conn, cursor = setup_database()

    try:
        while True:
            print(f"Fetching and processing weather data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            process_weather_data(conn, cursor)
            
            print("Checking alerts...")
            check_alerts(cursor)
            
            print("Calculating daily summaries...")
            summaries = calculate_daily_summary(cursor)
            
            print("Plotting daily summaries...")
            plot_daily_summaries(summaries)
            
            # Pause execution for the specified interval
            time.sleep(INTERVAL)
    
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
