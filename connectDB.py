import psycopg2
import os
from psycopg2.extras import DictCursor
import urllib.parse as urlparse

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


def get_connection():
    conn = psycopg2.connect(
                            #dbname="wlist",
                            #user="dimas",
                            #password="123456",
                            #host="db-course.cvjxeoubdpa4.eu-central-1.rds.amazonaws.com",
                            #cursor_factory=DictCursor
                            dbname=dbname,
                            user=user,
                            password=password,
                            host=host,
                            port=port,
                            cursor_factory=DictCursor
                            )
    return conn
