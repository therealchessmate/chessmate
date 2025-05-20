import psycopg2
from typing import Any, List, Tuple

class GCPostgresConnector:
    def __init__(self, db_name: str, user: str, password: str, host: str, port: int = 5432):
        self.connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        self.cursor.execute(query, params)

    def fetch_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
