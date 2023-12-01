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
import os
import json
display = Display(visible=0, size=(800, 800))  
display.start()

env_vars = os.environ['ALLSECRETS']

def get_all_keys(data, prefix="", keys_list=None):
    if keys_list is None:
        keys_list = []
    if isinstance(data, dict):
        for key, value in data.items():
            get_all_keys(value, prefix + key + '.', keys_list)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            get_all_keys(item, prefix + str(i) + '.', keys_list)
    else:
        keys_list.append(prefix[:-1])  # Add the key without the trailing dot to the list
    return keys_list

def decode_parts(input_string):
    parts = input_string.split('_')
    if len(parts) >= 3:
        decoded_second_part = bytes.fromhex(parts[1]).decode('utf-8')
        decoded_third_part = bytes.fromhex(parts[2]).decode('utf-8')
        return decoded_second_part, decoded_third_part
    else:
        return None, None

parsed_data = json.loads(env_vars)
jsonkeys = get_all_keys(parsed_data)

for key_combo in [keys for keys in jsonkeys if keys.startswith("ISP_")]:
    username, password = decode_parts(key_combo)
    print("Scraping " + username + "'s toddle...")
    scrape_toddle(username, password)


def scrape_toddle(MyUsername, MyPassword):  

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

    username_input.send_keys(MyUsername)
    password_input.send_keys(MyPassword)

    submit_button.click()

    time.sleep(2)
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

    actions = ActionChains(driver)
    macgyver = True
    while macgyver:
        driver.get("https://web.toddleapp.com/platform/3716/todos")
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
    
    filename = MyUsername.split("@")[0] + ".ics"
    with open(filename, 'w') as my_file:
        my_file.writelines(c.serialize_iter())
