from pytrends.request import TrendReq
import requests
import sys
import json
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

def get_weather_data_from_openmeteo(latitude, longitude, start_date, end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

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
    return daily_dataframe


def main():
    latitude = 42.2776
    longitude = -83.7409
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    # weather_data_from_visualcrossing = get_weather_data_from_visualcrossing(visualcrossing_api_key, location)
    weather_data_from_openmeteo = get_weather_data_from_openmeteo(latitude, longitude, start_date, end_date)

    if weather_data_from_openmeteo is not None:
        print("\nAverage Temperature of Days in 2023 Calendar Year:")
        # Convert 'date' column to string type
        weather_data_from_openmeteo['date'] = weather_data_from_openmeteo['date'].astype(str)
        # Extract year-month-date from the 'date' column
        weather_data_from_openmeteo['date'] = weather_data_from_openmeteo['date'].str.extract(r'^(\d{4}-\d{2}-\d{2})')
        
        
        weather_data_from_openmeteo['temperature_avg'] = (weather_data_from_openmeteo['temperature_2m_max'] + weather_data_from_openmeteo['temperature_2m_min']) / 2
        # Drop columns for min and max temperature
        weather_data_from_openmeteo.drop(columns=['temperature_2m_max', 'temperature_2m_min'], inplace=True)
        print(weather_data_from_openmeteo)


if __name__ == "__main__":
    main()

