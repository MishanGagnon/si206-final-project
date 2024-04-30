from db_utils import *
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    DB_NAME = 'test.db'
    conn = set_up_database(DB_NAME)
    cur = conn.cursor()

    # Create a new table to store the combined data
    cur.execute('''CREATE TABLE IF NOT EXISTS combined_data (
                    month INTEGER,
                    year INTEGER,
                    average_tigers REAL,
                    batting_average REAL
                    )''')

    # Insert combined data into the new table
    cur.execute('''INSERT INTO combined_data (month, year, average_tigers, batting_average)
                   SELECT iot.month, iot.year, iot.average_tigers, ba.batting_average
                   FROM
                       (SELECT strftime('%m', date) AS month, strftime('%Y', date) AS year, AVG(tigers) AS average_tigers 
                        FROM interest_over_time 
                        GROUP BY strftime('%Y', date), strftime('%m', date)) AS iot
                   JOIN
                       (SELECT Month AS month, Year AS year, BA AS batting_average 
                        FROM batting_average_by_month 
                        WHERE DateTime > '2020-11-01') AS ba
                   ON iot.month = ba.month AND iot.year = ba.year''')

    conn.commit()

    # Fetch and print the combined data
    # cur.execute("SELECT * FROM combined_data")
    # print(cur.fetchall())

    # Connect to the database
    conn = sqlite3.connect('test.db')

    # Read the combined data from the database into a DataFrame
    combined_data = pd.read_sql_query("SELECT average_tigers, batting_average FROM combined_data", conn)

    # Plot scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=combined_data, x='average_tigers', y='batting_average')
    sns.regplot(data=combined_data, x='average_tigers', y='batting_average', scatter=False, color='red', ci=None)  # Add regression line
    plt.title('Batting Average vs. Average Tigers')
    plt.xlabel('Average Tigers')
    plt.ylabel('Batting Average')
    plt.show()
    correlation_coefficient1 = combined_data['average_tigers'].corr(combined_data['batting_average'])
    print("Correlation Coefficient 1:", correlation_coefficient1)

    temperature_data = pd.read_sql_query("SELECT date, avg_temp_fahrenheit FROM avg_temp", conn)
    search_data = pd.read_sql_query("SELECT date, ice_cream FROM interest_over_time", conn)
    food_data = pd.read_sql_query("SELECT date, food_near_me FROM interest_over_time", conn)

    merged_data1 = pd.merge(temperature_data, search_data, on='date', how='inner')

    # Calculate correlation coefficient
    correlation_coefficient1 = merged_data1['avg_temp_fahrenheit'].corr(merged_data1['ice_cream'])
    print("Correlation Coefficient 2:", correlation_coefficient1)


    # Plot scatter plot with regression line
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_data1, x='avg_temp_fahrenheit', y='ice_cream')
    sns.regplot(data=merged_data1, x='avg_temp_fahrenheit', y='ice_cream', scatter=False, color='red', ci=None)  # Add regression line
    plt.title('Relation between Temperature and Ice Cream Searches in 2023')
    plt.xlabel('Average Temperature (Fahrenheit)')
    plt.ylabel('Number of Searches for "Ice Cream"')
    plt.show()

    # Read the food_near_me data from the database
    food_data = pd.read_sql_query("SELECT date, food_near_me FROM interest_over_time", conn)

    # Merge the temperature data with the food data
    merged_data2 = pd.merge(temperature_data, food_data, on='date', how='inner')

    # Calculate correlation coefficient
    correlation_coefficient2 = merged_data2['avg_temp_fahrenheit'].corr(merged_data2['food_near_me'])
    print("Correlation Coefficient 3:", correlation_coefficient2)

    # Plot scatter plot with regression line for food data
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=merged_data2, x='avg_temp_fahrenheit', y='food_near_me')
    sns.regplot(data=merged_data2, x='avg_temp_fahrenheit', y='food_near_me', scatter=False, color='green', ci=None)  # Add regression line
    plt.title('Relation between Temperature and Food Searches in 2023')
    plt.xlabel('Average Temperature (Fahrenheit)')
    plt.ylabel('Number of Searches for "Food Near Me"')
    plt.show()

    conn.close()

if __name__ == "__main__":
    main()
