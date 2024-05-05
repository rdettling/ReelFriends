import sqlite3
import glob


def run_sql_script(file_path, connection):
    """Run a SQL script file on the given database connection."""
    with open(file_path, "r") as sql_file:
        sql_script = sql_file.read()
    try:
        connection.executescript(sql_script)
        print(f"Successfully ran {file_path}")
    except Exception as e:
        print(f"Error occurred when running {file_path}: {str(e)}")


def main():
    # Path to the SQL directory
    sql_directory = "../sql/"
    # Path to the SQLite database
    db_path = "../sql/db.sqlite"

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    print("Connected to the database.")

    # Get all SQL files starting with 'create_'
    sql_files = glob.glob(f"{sql_directory}create_*.sql")
    for file_path in sql_files:
        run_sql_script(file_path, conn)

    # Close the connection to the database
    conn.close()
    print("Closed the database connection.")


if __name__ == "__main__":
    main()
