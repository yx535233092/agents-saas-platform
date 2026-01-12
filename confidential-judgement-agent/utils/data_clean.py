import pandas as pd
import sqlite3
import os


def data_clean():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "../../db/test.db"))
    query = "SELECT * FROM test"
    df = pd.read_sql_query(query, conn)
    print(df.info())
    conn.close()
    return df


if __name__ == "__main__":
    data_clean()
