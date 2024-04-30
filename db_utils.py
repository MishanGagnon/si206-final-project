#includes copilot written docstrings

import os
import sqlite3
import pandas as pd
def set_up_database(db_name):
    """
    Sets up a connection to the specified SQLite database.

    Parameters:
    - db_name (str): The name of the database file.

    Returns:
    - conn (sqlite3.Connection): The connection object to the database.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return conn

def create_table_from_df(df, table_name, conn):
    """
    Create a table in the database from a pandas DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to be stored in the table.
        table_name (str): The name of the table to be created.
        conn (sqlite3.Connection): The connection object to the SQLite database.

    Returns:
        None
    """
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    
    columns = []
    for col_name, dtype in df.dtypes.items():
        col_type = 'TEXT' 
        if pd.api.types.is_integer_dtype(dtype):
            col_type = 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            col_type = 'REAL'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_type = 'DATETIME'
        columns.append(f"{col_name} {col_type}")
    
    sql += ", ".join(columns)
    sql += ")"
    
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def get_oldest_date(table_name, date_col_name, conn):
    """
    Retrieves the oldest date from a specified table and column in a database.

    Args:
        table_name (str): The name of the table.
        date_col_name (str): The name of the column containing dates.
        conn: The database connection object.

    Returns:
        The oldest date as a string, or None if no date is found or an error occurs.
    """
    try:
        cur = conn.cursor()

        cur.execute(f"SELECT MIN({date_col_name}) FROM {table_name}")
        
        result = cur.fetchone()

        if result and result[0]:
            return result[0]
        else:
            return None

    except Exception as e:
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
    
    new_date = date + pd.Timedelta(days=days)
    
    return new_date.strftime('%Y-%m-%d')

def insert_data_from_df(df, table_name, date_col_name, conn):
    """
    Inserts data from a pandas DataFrame into a specified table in a SQLite database.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data to be inserted.
    - table_name (str): The name of the table in the database where the data will be inserted.
    - date_col_name (str): The name of the column in the DataFrame that contains the date values.
    - conn (sqlite3.Connection): The connection object to the SQLite database.

    Returns:
    None
    """

    cur = conn.cursor()
    df[date_col_name] = pd.to_datetime(df[date_col_name])
    df[date_col_name] = df[date_col_name].dt.strftime('%Y-%m-%d')
    placeholders = ', '.join(['?'] * len(df.columns))
    columns = ', '.join(df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    for row in df.itertuples(index=False, name=None):
        cur.execute(sql, row)
        conn.commit()
    
