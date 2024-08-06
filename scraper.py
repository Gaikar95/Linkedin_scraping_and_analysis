

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql
import time
import re

from connect_sql import init_database

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# Initialize the WebDriver
def init_driver():
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except Exception as e:
        print(e)
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service)
    return driver


# Function to log-in
def linkedin_login(driver, username, password):
    # LinkedIn login Url
    driver.get("https://www.linkedin.com/login")

    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(username)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    sign_in_button.click()


# Function to search with given keywords
def search_jobs(driver, job_title, location):
    search_url = f'https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}'
    driver.get(search_url)
    time.sleep(5)


# Function to scroll search results
def scroll_element(driver, element):
    scroll_increment = 300  # You can adjust this value for smoother scrolling
    scroll_pause_time = 0.3  # You can adjust this value for slower/faster scrolling

    current_height = 0
    last_height = driver.execute_script("return arguments[0].scrollHeight", element)
    while current_height < last_height:
        driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", element, scroll_increment)
        time.sleep(scroll_pause_time)
        current_height += scroll_increment
        last_height = driver.execute_script("return arguments[0].scrollHeight", element)


# Function to extract details from job post
def extract_job_details(driver, search_keyword, cursor):
    job_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__job-details--container")))

    # Extract job title
    try:
        job_title = job_container.find_element(By.XPATH, '//div/h1/a').text
    except:
        job_title = None

    # Extract job link
    try:
        job_link = job_container.find_element(By.XPATH, '//div/h1/a').get_attribute('href')
        job_id = re.search(r'/jobs/view/(\d+)/', job_link).group(1)

    except:
        job_link = None
        job_id = None

    # Extract company name
    try:
        company_name = job_container.find_element(By.CLASS_NAME,
                                                  "job-details-jobs-unified-top-card__company-name").find_element(
            By.TAG_NAME, "a").text
    except:
        company_name = None

    # Extract job location
    try:
        job_location = job_container.find_element(By.CSS_SELECTOR,
                                                  "div.job-details-jobs-unified-top-card__primary-description-container span").text
    except:
        job_location = None

    # Extract date posted
    try:
        date_posted = job_container.find_element(By.CSS_SELECTOR,
                                                 "div.job-details-jobs-unified-top-card__primary-description-container span:nth-child(3)").text
    except:
        date_posted = None

    # Extract number of applicants
    try:
        num_applicants = job_container.find_element(By.CSS_SELECTOR,
                                                    "div.job-details-jobs-unified-top-card__primary-description-container span:nth-child(5)").text
        num_applicants = ''.join([char for char in num_applicants if char.isdigit()])
    except:
        num_applicants = 0

    # Extract job insights
    try:
        job_insights = job_container.find_elements(By.CSS_SELECTOR,
                                                   "ul li.job-details-jobs-unified-top-card__job-insight")
        insights = [insight.text for insight in job_insights]
    except:
        insights = None

    # Extract job description
    try:
        job_description = job_container.find_element(By.CLASS_NAME, "jobs-description__container").text
    except:
        job_description = None

    insert_query = """
        INSERT INTO LinkedIn_jobs (job_id, Keywords, job_title, company_name, job_location, date_posted, num_applicants, insights, job_link, job_description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        job_id, search_keyword, job_title, company_name, job_location, date_posted, num_applicants,
        ', '.join(insights) if insights else None, job_link, job_description
    )
    try:
        cursor.execute(insert_query, data)
    except pymysql.MySQLError as e:
        print(f"Error inserting job details: {e}")


# Function to find and click the "next" button
def go_to_next_page(driver, n):
    print(n)
    try:
        # Find the pagination container
        pagination = driver.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')
        next_button = pagination.find_element(By.XPATH, "//button[contains(@aria-label, 'Page {}')]".format(n))
        next_button.click()
        time.sleep(2)
        return True
    except Exception as e:
        return False


def scrap(driver, job_title, location, database, processed_job_ids):
    cursor = database.cursor()
    search_jobs(driver, job_title, location)
    next_page = True
    n = 1
    while next_page:
        try:
            jobs_search_results = driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
            scroll_element(driver, jobs_search_results)
            job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
            for job in job_cards:
                job_id = job.get_attribute('data-job-id')
                if job_id in processed_job_ids:
                    print('already in extracted data set')
                else:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
                        job.click()
                        extract_job_details(driver, job_title, cursor)
                        processed_job_ids.add(job_id)
                        print('added job id to set')
                    except:
                        pass

            database.commit()
            n = n + 1
            next_page = go_to_next_page(driver, n)
        except Exception as e:
            print(e)
