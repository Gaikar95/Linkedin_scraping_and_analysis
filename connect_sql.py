import pymysql
import pandas as pd


def create_database():
    database = pymysql.connect(
        host="localhost",
        user="root",
        password="root"
    )

    with database.cursor() as cursor:
        # create new database
        try:
            cursor.execute("create database linkedin")
        except Exception as e:
            print(e)

        cursor.execute("use linkedin")

        # create linkedin_jobs table
        try:
            cursor.execute("""CREATE TABLE linkedin_jobs (
            job_id BIGINT PRIMARY KEY,
            Keywords VARCHAR(255),
            job_title VARCHAR(255),
            company_name VARCHAR(255),
            job_location VARCHAR(255),
            date_posted VARCHAR(255),
            num_applicants VARCHAR(255),
            insights TEXT,
            job_link TEXT,
            job_description TEXT
        )""")
        except pymysql.err.OperationalError as e:
            print(e)
    return database


def init_database():
    try:
        database = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="linkedin"
        )
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1049:
            database = create_database()

    return database


# Read the data from sql
def read_data():
    database = pymysql.connect(
        user='root',
        password='root',
        host='localhost',
        database='linkedin'
    )

    data = pd.read_sql("SELECT * FROM linkedin_jobs", database)

    # Close the connection
    database.close()
    return data
