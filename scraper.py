from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
import os, sys
from datetime import datetime
from ics import Calendar, Event
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

print("ALL ARGUMENTS:")
print(sys.argv)

username = sys.argv[1][1:]
password = sys.argv[2]

print("USERNAME: " + username)
print("PASSWORD: " + password)

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

username_input.send_keys(username + "@isp.cz")
password_input.send_keys(password)

submit_button.click()

time.sleep(2)

macgyver = True
while macgyver:
  driver.get("https://web.toddleapp.com/platform/3716/todos")
  
  actions = ActionChains(driver)
  
  def load_all_assignments():
      WebDriverWait(driver, 15).until(
          EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[1]"))
      )
      time.sleep(2)
  
      assignments_num = int(driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/div[2]').text)
      assignments = driver.find_elements(By.XPATH, "//*[starts-with(@class, 'FeedItem__container')]")
      bottom_of_assignments = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div/div[2]')
  
      while len(assignments) < assignments_num:
          driver.execute_script("arguments[0].scrollIntoView();", bottom_of_assignments)
          time.sleep(0.5)
          assignments = driver.find_elements(By.XPATH, "//*[starts-with(@class, 'FeedItem__container')]")
      return assignments, assignments_num
  
  assignments, assignments_num = load_all_assignments()
  assingment_data = []
  
  for assignment in assignments:
    name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[1]').text
    class_name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[2]').text
    due_date = assignment.find_element(By.XPATH, './div[2]/div[1]/div[2]').text
    assingment_data.append(tuple((name, class_name, due_date)))

  if '' in [assignment[2] for assignment in assingment_data]:
    assingment_data = []
  else:
    macgyver = False

for i in range(assignments_num):
    actions.move_to_element(assignments[i]).click().perform()
    link = driver.current_url
    assingment_data[i] = assingment_data[i] + (link,)
    driver.back()
    load_all_assignments()

def convert_date(input_date):
    without_day = input_date[input_date.find(',') + 1:].strip()
    date = without_day[:without_day.find(',')]
    time = without_day[without_day.find(',') + 1:].strip()
    date_formatted = datetime.strptime(date, "%d %b %Y").strftime("%Y-%m-%d")
    if ":" in time:
        time_formatted = datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")
    else:
        time_formatted = datetime.strptime(time, "%I %p").strftime("%H:%M:%S")
    return f"{date_formatted} {time_formatted}"

c = Calendar()

print([assignment[2] for assignment in assingment_data])

for assignment in assingment_data:
  e = Event()
  e.name = assignment[0]
  e.description = assignment[1] + "\n" + assignment[3]
  e.begin = e.end = convert_date(assignment[2])
  e.url = assignment[3]
  c.events.add(e)
  
filename = username + ".ics"
with open(filename, 'w') as my_file:
    my_file.writelines(c.serialize_iter())
