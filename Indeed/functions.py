import wget
import zipfile
import os
import requests
from datetime import date, timedelta

# Function to update our current Chrome version


def update_driver():
    # get the latest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text
    # build the donwload url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number + "/chromedriver_mac64.zip"

    # download the zip file using the url built above
    latest_driver_zip = wget.download(download_url, 'chromedriver.zip')

    # extract the zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
         zip_ref.extractall("../ChromeDriver_Path")  # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)

# Function to add "+" in the multiple-worded inputs


def url_string(string):
    output = ""
    for item in string.split(" "):
        if item != string.split(" ")[-1]:
            output = output + item + "+"
        else:
            output = output + item
    return output

# To convert the post date to real datetime
def date_to_calendar(x):
    lst = [int(s) for s in x.split() if s.isdigit()]
    if not lst:
        if "+" in x:
            return None
        else:
            return date.today()
    else:
        return date.today() - timedelta(days=int(lst[0]))


