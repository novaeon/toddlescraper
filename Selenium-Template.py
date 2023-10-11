from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
from datetime import datetime
from ics import Calendar, Event
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)

url = "https://web.toddleapp.com/platform?type=loginForm&usertype=student"
driver.get(url)

username_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[1]/div/div/div/div/div[2]/input')
password_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[2]/div[2]/div/div/div/div/input')
submit_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/button')

username_input.send_keys(os.environ['EMAIL'])
password_input.send_keys(os.environ['PASSWORD'])

submit_button.click()

wait = WebDriverWait(driver, 15)  
todos_button = wait.until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/button"))
)

todos_button.click()

wait = WebDriverWait(driver, 15) 
todo_list = wait.until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]"))
)

time.sleep(3)

assignments_num_el = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/div[2]')
assignments_num = int(assignments_num_el.text)
assignments = driver.find_elements(By.CLASS_NAME, 'FeedItem__container___RSNWD')
bottom_of_assignments = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]')

while len(assignments) < assignments_num:
  driver.execute_script("arguments[0].scrollIntoView();", bottom_of_assignments)
  time.sleep(1)
  assignments = driver.find_elements(By.CLASS_NAME, 'FeedItem__container___RSNWD')

assingment_data = []

for assignment in assignments:
  name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[1]').text
  class_name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[2]').text
  due_date = assignment.find_element(By.XPATH, './div[2]/div[1]/div[2]').text
  assingment_data.append(tuple((name, class_name, due_date)))

def convert_date(input_date):
    input_date_time = input_date[input_date.find(',') + 1:].strip()
    input_format = "%d %b %Y, %I %p"
    output_format = "%d %b %Y, %I:%M %p"
    try:
        datetime_obj = datetime.strptime(input_date_time, input_format)
        formatted_time = datetime_obj.strftime(output_format)
        input_date_time = formatted_time
    except ValueError:
        pass
    month_mapping = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    date_parts = input_date_time.split(",")
    date = date_parts[0].strip()
    time = date_parts[1].strip()
    day, month, year = date.split()
    formatted_date = f"{year}-{month_mapping[month]}-{day.zfill(2)}"
    formatted_time = datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")
    formatted_date_time = f"{formatted_date} {formatted_time}"
    return formatted_date_time


c = Calendar()

for assignment in assingment_data:
  e = Event()
  e.name = assignment[0]
  e.description = assignment[1]
  e.begin = e.end = convert_date(assignment[2])
  c.events.add(e)
  

with open('mytoddlecalendar.ics', 'w') as my_file:
    my_file.writelines(c.serialize_iter())
