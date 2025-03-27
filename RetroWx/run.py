import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import re

version = "0.0.0.1"

def query_weather_database(db_path, start_date, end_date):
    """
    Query the historical weather events database for events between start_date and end_date.
    
    Parameters:
        db_path (str): Path to the SQLite database file.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
        pd.DataFrame: DataFrame containing the query results.
    """
    conn = sqlite3.connect(db_path)
    query = """
        SELECT *
        FROM historical_weather
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def display_results(df):
    """
    Display the query results and plot a time series of temperature.
    
    For each row in the query result, display main weather values including:
      - date
      - location (formatted as coordinates)
      - temperature, precipitation, wind speed
      - additional_info as a description below the values.
    
    Parameters:
        df (pd.DataFrame): The historical weather data.
    """
    if df.empty:
        print("No weather events found for the specified date range.")
        return

    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])
    print("===========================")
    print("Historical Weather Event(s) entries found:")
    # Loop over the first 10 rows and print details
    for i, row in df.iterrows():
        print("-------------------------------------------------")
        print(f"Date: {row['date'].strftime('%Y-%m-%d')}")
        if 'location' in df.columns and pd.notnull(row['location']):
            # Format the coordinates nicely if needed
            formatted_coords = row['location']
            print(f"Location: {formatted_coords}")
        if 'temperature' in df.columns and pd.notnull(row['temperature']):
            print(f"Temperature: {row['temperature']} °C")
        if 'precipitation' in df.columns and pd.notnull(row['precipitation']):
            print(f"Precipitation: {row['precipitation']} mm")
        if 'wind_speed' in df.columns and pd.notnull(row['wind_speed']):
            print(f"Wind Speed: {row['wind_speed']} km/h")
        if 'wind_direction' in df.columns and pd.notnull(row['wind_direction']):
            print(f"Wind Direction: {row['wind_direction']}")
        if 'additional_info' in df.columns and pd.notnull(row['additional_info']):
            print(f"Description: {row['additional_info']}")
        print("-------------------------------------------------")
        if i >= 9:  # display only first 10 rows
            break



def main():
    print("Welcome to RetroWx!")
    print("A program/script that is a part of the TempestPy Weather Enthusiast Suite")
    print(f"Version {version}")
    print("by Blaine Palmer")
    print("===========================")
    
    # Fixed database path:
    db_path = "database/historicalweatherevents.db"
    print(f"Using database at: {db_path}")
    
    start_date = input("Enter the start date (YYYY/MM/DD): ").strip()
    end_date = input("Enter the end date (YYYY/MM/DD): ").strip()

    df = query_weather_database(db_path, start_date, end_date)
    display_results(df)

if __name__ == "__main__":
    main()
