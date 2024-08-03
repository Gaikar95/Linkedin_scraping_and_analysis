
from connect_sql import init_database
import scraper
from getpass import getpass


def main():
    # Job search parameters
    # List of job titles to search for
    job_titles = ['Data Scientist', 'Machine Learning Engineer', 'Business Intelligence Analyst',
                  'Data Engineer']
    # location
    locations = ['Mumbai','Pune']

    scrap_poll = input("Do you want to scrap data? Y/N")

    if scrap_poll == 'Y':
        driver = scraper.init_driver()
        # LinkedIn credentials
        username = input('Enter username:\n')
        password = getpass('Enter Password:\n')
        scraper.linkedin_login(driver, username, password)

        db = init_database()
        cursor = db.cursor()
        cursor.execute("select job_id from linkedin_jobs")
        keys = [key[0] for key in cursor.fetchall()]
        processed_job_ids = set(keys)

        for job_title in job_titles:
            for location in locations:
                scraper.scrap(driver, job_title, location, db, processed_job_ids)


if __name__ == "__main__":
    main()
