# Importing Selenium and all related modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Importing other libraries required
import time
import pandas as pd
from datetime import date, timedelta
import random

# Import all functions defined
from functions import *

# ________________________1. Getting the latest webdriver version_____________________
update_driver()

# ________________________2. Webdriver Instance_____________________
# Creating a webdriver instance
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
driver = webdriver.Chrome("../ChromeDriver_Path/chromedriver", chrome_options=options)

url = "https://www.indeed.com/worldwide"  # The Indeed URL is defined

# Opening the url we have just defined in our browser
driver.get(url)

# ________________________3. Scraping the list of countries_____________________
# We get a list containing all jobs that we have found..
countries_list = driver.find_element(By.ID, "page")
countries = countries_list.find_elements(By.TAG_NAME, "a")  # return a list
country_link_dict = {ii.text: ii.get_attribute("href") for ii in countries}

# ________________________4. Scraping the list of jobs_____________________
# Defining the job and the country
job_name = "Data Scientist"
country_name = "United States"

# Getting the corresponding URL for our country
url = country_link_dict[country_name]

# Adding + in case that are requird
job_name_url = url_string(job_name)
country_name_url = url_string(country_name)

# Defining the URL to find the job and the country
url = url.split("/?hl")[0] + "/jobs?q={0}&l={1}".format(job_name_url,country_name_url)

# Opening the url we have just defined in our browser
driver.get(url)  # Opening the url we have just defined in our browser

# ________________________5. Getting the number of job results_____________________
# We find how many jobs are offered.
jobs_num = driver.find_element(By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount").get_attribute("innerText")
jobs_num = jobs_num.replace(' jobs', '')

if ',' in jobs_num and (jobs_num := jobs_num.replace(',', '')).isdigit():
    jobs_num = int(jobs_num)

# ________________________6. Browsing all jobs_____________________
# Void lists to store the data.
job_title_list = [];
job_company_list = [];
job_location_list = [];
job_salary_list = [];
job_type_list = [];
job_date_list = [];
job_description_list = [];
job_link_list = [];
job_id_list = [];

# The next button is defined.
next_button_xpath = '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[6]/a'

num_jobs_scraped = 0

while num_jobs_scraped < 1000:

    # The job browsing is started
    job_page = driver.find_element(By.ID, "mosaic-jobResults")
    jobs = job_page.find_elements(By.CLASS_NAME, "job_seen_beacon")  # return a list
    num_jobs_scraped = num_jobs_scraped + len(jobs)

    for ii in jobs:
        # Finding the job title and its related elements
        job_title = ii.find_element(By.CLASS_NAME, "jobTitle")
        job_title_list.append(job_title.text)
        job_link_list.append(job_title.find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
        job_id_list.append(job_title.find_element(By.CSS_SELECTOR, "a").get_attribute("id"))

        # Finding the company name and location
        job_company_list.append(ii.find_element(By.CLASS_NAME, "companyName").text)
        job_location_list.append(ii.find_element(By.CLASS_NAME, "companyLocation").text)
        # Finding the posting date
        job_date_list.append(ii.find_element(By.CLASS_NAME, "date").text)

        # Trying to find the salary element. If it is not found, a None will be returned.
        try:
            job_salary_list.append(ii.find_element(By.CLASS_NAME, "salary-snippet-container").text)

        except:
            try:
                job_salary_list.append(ii.find_element(By.CLASS_NAME, "estimated-salary").text)
            except:
                job_salary_list.append(None)

        # We wait a random amount of seconds to imitate a human behavior.
        time.sleep(random.random())

        # Click the job element to get the description
        job_title.click()

        # Wait for a bit for the website to charge (again with a random behavior)
        time.sleep(1.5 + random.random())

        # Find the job description. If the element is not found, a None will be returned.
        try:
            job_description_list.append(driver.find_element(By.ID, "jobDescriptionText").text)

        except:
            job_description_list.append(None)

    time.sleep(1.5 + random.random())

    # We press the next button.
    driver.find_element(By.XPATH, next_button_xpath).click()

    # The button element is updated to the 7th button instead of the 6th.
    next_button_xpath = '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[7]/a'

# ________________________7.Creating a DataFrame_____________________
country_list = [country_name] * len(job_title_list)
job_name_list = [job_name] * len(job_title_list)
scraped_date_list = [date.today()] * len(job_title_list)

country_list = [country_name] * len(job_title_list)
job_name_list = [job_name] * len(job_title_list)
scraped_date_list = [date.today()] * len(job_title_list)

indeed_job_data = pd.DataFrame({
    'job_id': job_id_list,
    'scraped_date': scraped_date_list,
    'country': country_list,
    'job_name': job_name_list,
    'job_post_date': job_date_list,
    'job_company': job_company_list,
    'job_title': job_title_list,
    'job_location': job_location_list,
    'job_description': job_description_list,
    'job_link': job_link_list,
    'job_salary': job_salary_list,
    # 'job_type': job_type_list,

})

driver.quit()

# ________________________7.Computing the calendar job post time_____________________
indeed_job_data["calendar_job_post_date"] = indeed_job_data.apply(lambda x: date_to_calendar(x["job_post_date"]), axis=1)
indeed_job_data.to_csv("Output/{0}_{1}_".format(country_name, job_name) + "_ddbb.csv")