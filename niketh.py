import pybaseball
import pandas as pd
import numpy as np
from db_utils import *

def get_team_batting_average_by_month(team, start_date, end_date):
    try:
        # Create an empty DataFrame to store team stats
        team_stats = pd.DataFrame()

        # set start_date and end_date to proper format
        start_year_temp = start_date[0:4]
        start_year = int(start_year_temp)

        end_date_temp = end_date[0:4]
        end_year = int(end_date_temp)  
        
        # Iterate over the specified range of years
        for year in range(start_year, end_year + 1):
            # Fetch team game logs for the year
            yearly_logs = pybaseball.team_game_logs(year, team)
            
            # Convert date to datetime and extract month
            yearly_logs['Date'] = pd.to_datetime(yearly_logs['Date'], format='%b %d', errors='coerce')
            if yearly_logs['Date'].isnull().all():
                raise ValueError("Failed to parse any dates for the year {}.".format(year))
            
            yearly_logs['Month'] = yearly_logs['Date'].dt.month
            
            # Group by month and calculate cumulative statistics
            monthly_stats = yearly_logs.groupby('Month').agg({
                'PA': 'sum',  # Total plate appearances in the month
                'AB': 'sum',  # Total at-bats in the month
                'H': 'sum'   # Total hits in the month
            }).reset_index()
            
            # Calculate batting average (H/AB)
            monthly_stats['BA'] = monthly_stats.apply(lambda x: x['H'] / x['AB'] if x['AB'] != 0 else np.nan, axis=1)
            monthly_stats['Year'] = year  # Add year for tracking
            monthly_stats['TeamID'] = 19
            
            # Remove rows with null or inf values in the batting average column
            monthly_stats = monthly_stats.replace([np.inf, -np.inf], np.nan).dropna(subset=['BA'])
            
            # Convert 'Month' column to int64 type
            monthly_stats['Month'] = monthly_stats['Month'].astype('int64')
            
            # Create a new column for datetime with default values for day and time
            monthly_stats['DateTime'] = pd.to_datetime(monthly_stats[['Year', 'Month']].assign(Day=1))
            
            # Append to the main DataFrame
            team_stats = pd.concat([team_stats, monthly_stats], ignore_index=True)
        
        return team_stats
    except Exception as e:
        print("An error occurred:", e)

def create_team_dataframe():
    # List of MLB teams and their abbreviations
    mlb_teams = [
        {"Team": "Arizona Diamondbacks", "Abbreviation": "ARI"},
        {"Team": "Atlanta Braves", "Abbreviation": "ATL"},
        {"Team": "Baltimore Orioles", "Abbreviation": "BAL"},
        {"Team": "Boston Red Sox", "Abbreviation": "BOS"},
        {"Team": "Chicago White Sox", "Abbreviation": "CHW"},
        {"Team": "Chicago Cubs", "Abbreviation": "CHC"},
        {"Team": "Cincinnati Reds", "Abbreviation": "CIN"},
        {"Team": "Cleveland Guardians", "Abbreviation": "CLE"},
        {"Team": "Colorado Rockies", "Abbreviation": "COL"},
        {"Team": "Detroit Tigers", "Abbreviation": "DET"},
        {"Team": "Houston Astros", "Abbreviation": "HOU"},
        {"Team": "Kansas City Royals", "Abbreviation": "KCR"},
        {"Team": "Los Angeles Angels", "Abbreviation": "LAA"},
        {"Team": "Los Angeles Dodgers", "Abbreviation": "LAD"},
        {"Team": "Miami Marlins", "Abbreviation": "MIA"},
        {"Team": "Milwaukee Brewers", "Abbreviation": "MIL"},
        {"Team": "Minnesota Twins", "Abbreviation": "MIN"},
        {"Team": "New York Yankees", "Abbreviation": "NYY"},
        {"Team": "New York Mets", "Abbreviation": "NYM"},
        {"Team": "Oakland Athletics", "Abbreviation": "OAK"},
        {"Team": "Philadelphia Phillies", "Abbreviation": "PHI"},
        {"Team": "Pittsburgh Pirates", "Abbreviation": "PIT"},
        {"Team": "San Diego Padres", "Abbreviation": "SDP"},
        {"Team": "San Francisco Giants", "Abbreviation": "SFG"},
        {"Team": "Seattle Mariners", "Abbreviation": "SEA"},
    ]

    # Create DataFrame
    team_df = pd.DataFrame(mlb_teams)

    # Assign unique numbers to each team
    team_df['TeamID'] = range(1, len(team_df) + 1)

    return team_df

def insert_data_simple(df, table_name, conn):

    # Create a cursor object using the connection
    cur = conn.cursor()
    # Prepare the INSERT INTO statement
    placeholders = ', '.join(['?'] * len(df.columns))
    columns = ', '.join(df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    # Insert each row from the DataFrame
    for row in df.itertuples(index=False, name=None):
        cur.execute(sql, row)
        conn.commit()
    
    # Commit the transactions

DB_NAME = "test.db"
conn = set_up_database(DB_NAME)

team_dataframe = create_team_dataframe()
create_table_from_df(team_dataframe, "team_index", conn)
insert_data_simple(team_dataframe, "team_index", conn)

TABLE_NAME = "batting_average_by_month"
team = "NYM"
end = "2023-01-01"

# def pull_25_new_search(conn, table_name):
oldestDate = get_oldest_date(TABLE_NAME,'date',conn)
if oldestDate == None:
    oldestDate = '2023-01-01'

batting_averages_by_month = get_team_batting_average_by_month(team, shift_date(oldestDate,-1095), oldestDate)

create_table_from_df(batting_averages_by_month, TABLE_NAME, conn)
insert_data_from_df(batting_averages_by_month, TABLE_NAME,'DateTime', conn)

cur = conn.cursor()

# Execute the SELECT query
cur.execute("SELECT * FROM batting_average_by_month")

# Fetch and print the results
print(cur.fetchall())

# Example usage
# team_dataframe = create_team_dataframe()
# print(team_dataframe)


# Example usage
# team = 'NYM'  # New York Mets (using Fangraphs team ID)
# start = "2000-01-01"  # Fetch data from 2018 to 2020 for now
# end = "2020-01-01"

# Get team batting averages by month
# batting_averages_by_month = get_team_batting_average_by_month(team, start, end)
# batting_averages_by_month.info()
# if not batting_averages_by_month.empty:m
#     print(batting_averages_by_month)
# else:
#     print("Unable to retrieve batting averages by month.")