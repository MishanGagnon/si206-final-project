import requests
import sys
import json
from db_utils import *
import openmeteo_requests
import pandas as pd
from retry_requests import retry

def get_weather_data(latitude, longitude, start_date, end_date):
    # Setup the Open-Meteo API client without caching
    session = requests.Session()
    openmeteo = openmeteo_requests.Client(session=session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "ms",
        "timezone": "America/Chicago"
    }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min

    daily_dataframe = pd.DataFrame(data=daily_data)

    # Calculate average temperature
    daily_dataframe['avg_temp_fahrenheit'] = (daily_dataframe['temperature_2m_max'] + daily_dataframe['temperature_2m_min']) / 2
    # Drop columns for min and max temperature
    daily_dataframe.drop(columns=['temperature_2m_max', 'temperature_2m_min'], inplace=True)
    
    daily_dataframe.info()
    
    DB_NAME = "yash.db"
    TABLE_NAME = "avg_temp"
    conn = set_up_database(DB_NAME)
    
    # Rename the column in the DataFrame
    daily_dataframe.rename(columns={'avg_temp (fahrenheit)': 'avg_temp_fahrenheit'}, inplace=True)

    # Adjust the table creation to reflect the new column name
    create_table_from_df(daily_dataframe, TABLE_NAME, conn)

    # Insert data into the table
    insert_data_from_df(daily_dataframe, TABLE_NAME, 'date', conn)

    cur = conn.cursor()

    # Execute the SELECT query
    cur.execute("SELECT * FROM avg_temp")
    
    return daily_dataframe


def main():
    latitude = 42.3314
    longitude = -83.045753
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    weather_data_from_openmeteo = get_weather_data(latitude, longitude, start_date, end_date)

    if weather_data_from_openmeteo is not None:
        print("\nAverage Temperature of Days in 2023 Calendar Year:")
        print(weather_data_from_openmeteo)


if __name__ == "__main__":
    main()
