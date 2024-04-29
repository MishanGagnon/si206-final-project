import pybaseball
import pandas as pd

def get_team_batting_average_by_month(team, start_year, end_year):
    try:
        # Create an empty DataFrame to store team stats
        team_stats = pd.DataFrame()
        
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
            monthly_stats['BA'] = monthly_stats['H'] / monthly_stats['AB']
            monthly_stats['Year'] = year  # Add year for tracking
            monthly_stats['teamIDfg'] = team  # Add team ID for tracking
            
            # Append to the main DataFrame
            team_stats = pd.concat([team_stats, monthly_stats], ignore_index=True)
        
        return team_stats[['Year', 'Month', 'teamIDfg', 'PA', 'AB', 'H', 'BA']]
    
    except Exception as e:
        print("An error occurred:", e)

# Example usage
team = 'NYM'  # New York Yankees (using Fangraphs team ID)
start_year = 2015  # Fetch data from 2018 to 2020 for now
end_year = 2020

# Get team batting averages by month
batting_averages_by_month = get_team_batting_average_by_month(team, start_year, end_year)
if batting_averages_by_month is not None:
    print(batting_averages_by_month)
else:
    print("Unable to retrieve batting averages by month.")
