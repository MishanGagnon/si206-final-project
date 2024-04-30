import os
import sqlite3
import pandas as pd
def set_up_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return conn

def create_table_from_df(df, table_name, conn):
    # Start the CREATE TABLE statement
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    
    # Add columns with appropriate data types
    columns = []
    for col_name, dtype in df.dtypes.items():
        col_type = 'TEXT'  # Default type
        if pd.api.types.is_integer_dtype(dtype):
            col_type = 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            col_type = 'REAL'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_type = 'DATETIME'
        # Add column specification
        columns.append(f"{col_name} {col_type}")
    
    # Complete the SQL statement
    sql += ", ".join(columns)
    sql += ")"
    
    # Execute the SQL statement
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def get_oldest_date(table_name, date_col_name, conn):
    try:
        # Create a cursor object using the connection
        cur = conn.cursor()

        # Execute the query to find the oldest date
        cur.execute(f"SELECT MIN({date_col_name}) FROM {table_name}")
        
        # Fetch the result
        result = cur.fetchone()

        # Check if the result is not None and contains a date
        if result and result[0]:
            return result[0]
        else:
            return None

    except Exception as e:
        # Handle exceptions, which could occur if the table does not exist or query fails
        return None

def shift_date(date_str, days):
    """
    Shifts a given date by a specified number of days using pandas.
    
    Parameters:
    date_str (str): The date in 'YYYY-MM-DD' format.
    days (int): The number of days to shift the date. Negative for past, positive for future.
    
    Returns:
    str: The shifted date in 'YYYY-MM-DD' format.
    """
    date = pd.to_datetime(date_str)
    
    # Create a Timedelta and shift the date by the specified number of days
    new_date = date + pd.Timedelta(days=days)
    
    # Convert the Timestamp back to a string in 'YYYY-MM-DD' format
    return new_date.strftime('%Y-%m-%d')

def insert_data_from_df(df, table_name, date_col_name, conn):

    # Create a cursor object using the connection
    cur = conn.cursor()
    df[date_col_name] = pd.to_datetime(df[date_col_name])
    df[date_col_name] = df[date_col_name].dt.strftime('%Y-%m-%d')
    # Prepare the INSERT INTO statement
    placeholders = ', '.join(['?'] * len(df.columns))
    columns = ', '.join(df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    # Insert each row from the DataFrame
    for row in df.itertuples(index=False, name=None):
        cur.execute(sql, row)
        conn.commit()
    
    # Commit the transactions