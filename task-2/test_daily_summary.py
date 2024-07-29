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
        
        # Check that summaries contain the expected cities
        self.assertIn('Delhi', summaries)
        self.assertIn('Mumbai', summaries)

        # Check summary for 'Delhi'
        delhi_summary = summaries['Delhi']
        self.assertEqual(len(delhi_summary['dates']), 1)
        self.assertEqual(delhi_summary['dates'][0], '2023-01-01')
        self.assertAlmostEqual(delhi_summary['avg_temps'][0], 29.0)
        self.assertEqual(delhi_summary['max_temps'][0], 32.0)
        self.assertEqual(delhi_summary['min_temps'][0], 28.0)

        # Check summary for 'Mumbai'
        mumbai_summary = summaries['Mumbai']
        self.assertEqual(len(mumbai_summary['dates']), 1)
        self.assertEqual(mumbai_summary['dates'][0], '2023-01-01')
        self.assertAlmostEqual(mumbai_summary['avg_temps'][0], 31.0)
        self.assertEqual(mumbai_summary['max_temps'][0], 31.0)
        self.assertEqual(mumbai_summary['min_temps'][0], 31.0)

    def tearDown(self):
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
