import sqlite3
import sys

# Check if the table name is provided
if len(sys.argv) != 2:
    print("Usage: python drop_table.py <table_name>")
    sys.exit(1)

# The table name to drop
table_name = sys.argv[1]

# Path to the SQLite database
db_path = "../sql/db.sqlite"

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object using the connection
cursor = conn.cursor()

# SQL command to drop the specified table
sql_drop_table = f"DROP TABLE IF EXISTS {table_name};"

try:
    # Execute the SQL command
    cursor.execute(sql_drop_table)
    # Commit the changes
    conn.commit()
    print(f"Table '{table_name}' has been dropped successfully.")
except Exception as e:
    # Print any errors that occur
    print("An error occurred:", e)
finally:
    # Close the connection to the database
    conn.close()
