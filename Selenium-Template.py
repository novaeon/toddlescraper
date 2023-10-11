from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
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
    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]"))
)

wait = WebDriverWait(driver, 15)  # Adjust the timeout as needed
assignments_num = wait.until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/text()'))
)

assignments = driver.find_elements(By.CLASS_NAME, 'FeedItem__container___RSNWD')


while len(assignments) < assignments_num:
  todo_list.send_keys(Keys.PAGE_DOWN)
  assignments = driver.find_elements(By.CLASS_NAME, 'FeedItem__container___RSNWD')

assingment_data = []

for assignment in assignments:
  name = assignment.find_element(By.CLASS_NAME, 'FeedItem__assessmentName___1hg-J heading-6').text
  class_name = assignment.find_element(By.CLASS_NAME, 'FeedItem__bottomText___1pSO3 FeedItem__bottomTextTitle___2YBmw').text
  due_date = assignment.find_element(By.CLASS_NAME, 'FeedItem__bottomText___1pSO3 text-body-2').text
  assignment_data.append(tuple([name, class_name, due_date]))

string_ass = " ".join(str(x) for x in assingment_data)

with open('./GitHub_Action_Results.txt', 'w') as f:
    f.write(f"This was written with a GitHub action {string_ass}")
