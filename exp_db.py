import psycopg2
from psycopg2 import sql
from pathlib import Path

def execute_schema(host, db_name, user, password, port) -> None:
    """
    Main function to load environment variables, establish a connection to the PostgreSQL database,
    read and execute the schema SQL script, and close the database connection.
    """
    
    conn = psycopg2.connect(host=host, database=db_name, user=user, password=password, port=port)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
    """)

  
    with open('metrics.sql', 'r') as schema_file:
            script = schema_file.read()
            cursor.execute(script)
    conn.commit()
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
     execute_schema('localhost', 'backtest', 'postgres', '1234567', '5432') 