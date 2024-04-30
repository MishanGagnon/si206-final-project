from db_utils import *
def main():
    DB_NAME = 'test.db'
    conn = set_up_database(DB_NAME)
    cur = conn.cursor()

    # calculation for interest_over_time
    # Open a text file for writing
    with open('calculations.txt', 'w') as file:
        
        # calculations for pytrends
        cur.execute("SELECT AVG(ice_cream) FROM interest_over_time")
        file.write(f"Caluculation for pytrends, average interest for ice cream out of a hundred\n")
        file.write(f"Average google trends interest in ice cream: {cur.fetchone()[0]}/100\n\n")

        #calulation mean battting avg in 2022 for mets
        cur.execute("""
        SELECT AVG(b.BA), t.Team
        FROM batting_average_by_month b
        JOIN team_index t ON b.TeamID = t.TeamID
        WHERE Year BETWEEN 2022 AND 2023
        """)
        file.write(f"calulation mean battting avg in 2022 for mets from baseball API\n")
        ba, team = cur.fetchone()
        file.write(f"{team} batting average is {round(ba,3)}\n\n")

        # calculations for weather data
        cur.execute("SELECT COUNT(*) FROM avg_temp")
        file.write(f"How many weather measurements do we have recorded\n")
        file.write(f"Temp Measurements: {cur.fetchone()[0]}\n\n")

if __name__ == "__main__":
    main()