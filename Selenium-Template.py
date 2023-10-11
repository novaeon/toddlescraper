from selenium import webdriver
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

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

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

# Find the username and password input fields and submit button by their names
username_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[1]/div/div/div/div/div[2]/input')
password_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[1]/div[2]/div[2]/div/div/div/div/input')
submit_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/button')

# Enter the username and password
username_input.send_keys("102869@isp.cz")
password_input.send_keys("david&vahe")

# Submit the form
submit_button.click()

wait = WebDriverWait(driver, 15)  # Adjust the timeout as needed
todos_button = wait.until(
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/button"))
)

todos_button.click()

wait = WebDriverWait(driver, 15)  # Adjust the timeout as needed
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
    date_string = input_date[input_date.find(',') + 1:].strip()
    date = datetime.strptime(date_string, '%d %b %Y, %I %p')
    # Format the date string using datetime.strftime
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date

c = Calendar()

for assignment in assingment_data:
  e = Event()
  e.name = assignment[0]
  e.description = assignment[1]
  e.begin = e.end = convert_date(assignment[2])
  c.events.add(e)
  

with open('mytoddlecalendar.ics', 'w') as my_file:
    my_file.writelines(c.serialize_iter())
