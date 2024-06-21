import psycopg2
from psycopg2 import sql
from pathlib import Path


def save_db(data, table, columns):

    conn = psycopg2.connect(host='localhost', 
                            database='back_test', 
                            user='postgres', 
                            password='1234567', 
                            port='5432')
    cursor = conn.cursor()

    if table == 'scene':
        id = columns['id']
        strategy = columns['strategy']
        start_Date = columns['start_Date']
        end_date = columns['end_date']

        cursor.execute(
            f"INSERT INTO {table} (id, strategy, start_Date, end_date) VALUES (%s, %s, %s, %s,)",
            (id, strategy, start_Date, end_date)
        )

    else:
        id = columns['id']
        sharpe_ratio = columns['sharpe_ratio']
        total_return = columns['total_return']
        average_return = columns['average_return']
        total_drawdown = columns['total_drawdown']
        total_duration = columns['total_duration']

        cursor.execute(
            f"INSERT INTO {table} (id, sharpe_ratio, total_return, average_return, total_drawdown, total_duration) VALUES (%s, %s, %s, %s, %s, %s)",
            (id, sharpe_ratio, total_return, average_return, total_drawdown, total_duration)
        )
