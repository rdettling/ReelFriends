import pandas as pd
import sqlite3

# Path to the CSV file
csv_file_path = "movies_clean.csv"

# Path to the SQLite database
db_path = "../sql/db.sqlite"

# Read the CSV file into a DataFrame

df = pd.read_csv(csv_file_path)

# Replace NaN with None for proper NULL handling in SQLite
df = df.where(pd.notnull(df), None)

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Insert data into the database using a transaction
with conn:
    # Disable the default SQLite behavior of starting a transaction
    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )  # Optional: enforce foreign key constraints
    df.to_sql("movies", conn, if_exists="append", index=False)

# Close the connection to the database
conn.close()

print("Data has been successfully inserted into the database.")
