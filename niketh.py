import pybaseball
import pandas as pd
import numpy as np

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
            monthly_stats['teamIDfg'] = team  # Add team ID for tracking
            
            # Remove rows with null or inf values in the batting average column
            monthly_stats = monthly_stats.replace([np.inf, -np.inf], np.nan).dropna(subset=['BA'])
            
            # Convert 'Month' column to int64 type
            monthly_stats['Month'] = monthly_stats['Month'].astype('int64')
            
            # Create a new column for datetime with default values for day and time
            monthly_stats['DateTime'] = pd.to_datetime(monthly_stats[['Year', 'Month']].assign(Day=1))
            
            # Append to the main DataFrame
            team_stats = pd.concat([team_stats, monthly_stats], ignore_index=True)
        
        return team_stats[['DateTime', 'Year', 'Month', 'teamIDfg', 'PA', 'AB', 'H', 'BA']]
    
    except Exception as e:
        print("An error occurred:", e)

# Example usage
team = 'NYM'  # New York Mets (using Fangraphs team ID)
start = "2019-01-01"  # Fetch data from 2018 to 2020 for now
end = "2020-01-01"

# Get team batting averages by month
batting_averages_by_month = get_team_batting_average_by_month(team, start, end)
batting_averages_by_month.info()
if not batting_averages_by_month.empty:
    print(batting_averages_by_month)
else:
    print("Unable to retrieve batting averages by month.")
