import pymysql


def create_dataset():
    database = pymysql.connect(
        host="localhost",
        user="root",
        password="root"
    )

    cursor = database.cursor()

    # create new database
    try:
        cursor.execute("create database linkedin")
    except Exception as e:
        print(e)

    cursor.execute("use linkedin")

    # create linkedin_jobs table
    try:
        cursor.execute("""CREATE TABLE linkedin_jobs (
        job_id VARCHAR(255) PRIMARY KEY,
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


def init_database():
    database = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="linkedin"
    )

    return database, database.cursor()
