import psycopg2
from psycopg2.extras import DictCursor


def get_connection():
    conn = psycopg2.connect(dbname="wlist",
                            user="dimas",
                            password="123456",
                            host="db-course.cvjxeoubdpa4.eu-central-1.rds.amazonaws.com"#,
                            #cursor_factory=DictCursor
                            )
    return conn
