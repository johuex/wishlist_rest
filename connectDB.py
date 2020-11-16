import psycopg2


def get_connection():
    conn = psycopg2.connect(host='db-course.cvjxeoubdpa4.eu-central-1.rds.amazonaws.com',
                            user='dimas',
                            password='?',
                            dbname='wlist')
    return conn
