from pytrends.request import TrendReq
from db_utils import *
import matplotlib.pyplot as plt

# Initialize a TrendReq object
pytrend = TrendReq(hl='en-US', tz=360)  # 'hl' is the host language, 'tz' is the timezone offset

# Define the search keyword and the region
keyword = 'ice_cream'
geo = 'US-MI-505'  # Michigan, USA as the region, you might need to adjust this for more specific local data

# Build the payload
pytrend.build_payload(kw_list=[keyword], geo=geo, timeframe='today 5-y')  # Adjust timeframe as needed

# Get interest over time
interest_over_time_df = pytrend.interest_over_time()
interest_over_time_df.drop('isPartial', axis =1, inplace=True)
interest_over_time_df = interest_over_time_df.reset_index()
interest_over_time_df.columns = interest_over_time_df.columns.str.replace(' ', '_', regex=True)

DB_NAME = "test.db"
TABLE_NAME = "interest_over_time"
conn = set_up_database(DB_NAME)
create_table_from_df(interest_over_time_df, TABLE_NAME, conn)
insert_data_from_df(interest_over_time_df, TABLE_NAME,'date', conn)

cur = conn.cursor()

# Execute the SELECT query
cur.execute("SELECT * FROM interest_over_time")

# Fetch and print the results
print(cur.fetchall())