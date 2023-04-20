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
driver = webdriver.Chrome("ChromeDriver_Path/chromedriver", chrome_options=options)

url = "https://www.indeed.com/worldwide"  # The Indeed URL is defined

# Opening the url we have just defined in our browser
driver.get(url)

# ________________________3. Scraping the list of countries_____________________
# We get a list containing all jobs that we have found.
countries_list = driver.find_element(By.ID, "page")
countries = countries_list.find_elements(By.TAG_NAME, "a")  # return a list
country_link_dict = {ii.text: ii.get_attribute("href") for ii in countries}

# ________________________4. Scraping the list of jobs_____________________
# Define job_name and country_name
job_name = "Data Scientist"
country_name = "United States"

# Get the country specific URL string
url = country_link_dict[country_name]
#  Make sure our job_name and country_name are strings for the URL
job_name_url = url_string(job_name)
country_name_url = url_string(country_name)

url = "https://www.indeed.com/jobs?q={0}&l={1}".format(job_name_url, country_name_url)
driver.get(url)  # Opening the url we have just defined in our browser

# ________________________5. Getting the number of job results_____________________
# We find how many jobs are offered.
jobs_num = driver.find_element(By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount").get_attribute("innerText")
jobs_num = jobs_num.replace(' jobs', '')

if ',' in jobs_num and (jobs_num := jobs_num.replace(',', '')).isdigit():
    jobs_num = int(jobs_num)

# ________________________6. Browsing all jobs_____________________
job_title_list = []
job_company_list = []
job_location_list = []
job_salary_list = []
job_type_list = []
job_date_list = []
job_description_list = []
job_link_list = []
job_id_list = []
next_button_xpath = '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[6]/a'

num_jobs_scraped = 0

while num_jobs_scraped < 15:

    job_page = driver.find_element(By.ID, "mosaic-jobResults")
    jobs = job_page.find_elements(By.CLASS_NAME, "job_seen_beacon")  # return a list
    num_jobs_scraped = num_jobs_scraped + len(jobs)

    for ii in jobs:
        job_title_list.append(ii.find_element(By.CLASS_NAME, "jobTitle").text)
        job_company_list.append(ii.find_element(By.CLASS_NAME, "companyName").text)
        job_location_list.append(ii.find_element(By.CLASS_NAME, "companyLocation").text)
        job_date_list.append(ii.find_element(By.CLASS_NAME, "date").text)
        job_link_list.append(
            ii.find_element(By.CLASS_NAME, "jobTitle").find_element(By.CSS_SELECTOR, "a").get_attribute("href"))
        job_id_list.append(
            ii.find_element(By.CLASS_NAME, "jobTitle").find_element(By.CSS_SELECTOR, "a").get_attribute("id"))

        # Click the job element to get the description
        ii.find_element(By.CLASS_NAME, "jcs-JobTitle").click()
        # Wait for a bit for the website to charge
        time.sleep(1 + random.random())

        # Find the job description
        try:
            job_description_list.append(driver.find_element(By.ID, "jobDescriptionText").text)

        except:
            job_description_list.append(None)

        time.sleep(1 + random.random())

        try:
            job_salary_list.append(ii.find_element(By.CLASS_NAME, "salary-snippet-container").text)

        except:
            try:
                job_salary_list.append(ii.find_element(By.CLASS_NAME, "estimated-salary").text)
            except:
                job_salary_list.append(None)

        try:
            job_type_list.append(ii.find_element(By.CLASS_NAME, "attribute_snippet").text)
        except:
            job_type_list.append(None)

        # ii.find_element(By.CLASS_NAME,"jcs-JobTitle").click()

    time.sleep(1.5 + random.random())
    driver.find_element(By.XPATH, next_button_xpath).click()
    next_button_xpath = '//*[@id="jobsearch-JapanPage"]/div/div/div[5]/div[1]/nav/div[7]/a'

# ________________________7.Creating a DataFrame_____________________
country_list = [country_name] * len(job_title_list)
job_name_list = [job_name] * len(job_title_list)
scraped_date_list = [date.today()] * len(job_title_list)

indeed_job_data = pd.DataFrame({
    'job_id': job_id_list,
    'scraped_date': scraped_date_list,
    'country': country_list,
    'job_name': job_name_list,
    'job_post_date': job_title_list,
    'job_company': job_company_list,
    'job_title': job_title_list,
    'job_location': job_location_list,
    'job_description': job_description_list,
    'job_link': job_link_list,
    'job_salary': job_salary_list,
    # 'job_type': job_type_list,

})
indeed_job_data.to_csv("Output/{0}_{1}_".format(country_name, job_name) + "_ddbb.csv")
driver.quit()
