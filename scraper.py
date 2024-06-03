from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
import os, sys
from pyvirtualdisplay import Display
from datetime import datetime, timedelta
from ics import Calendar, Event
import os
import json

display = Display(visible=0, size=(1920, 1080))  
display.start()

env_vars = os.environ['ALLSECRETS']

def scrape_toddle(MyUsername, MyPassword):  

    chromedriver_autoinstaller.install()
    chrome_options = webdriver.ChromeOptions()
    options = [
        "--window-size=1200,1200",
        "--ignore-certificate-errors"
    ]
    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(options = chrome_options)
    actions = ActionChains(driver)


    def load_all_assignments():

        WebDriverWait(driver, 60).until( # Wait for assignment container to load
            EC.presence_of_element_located((By.XPATH, "//*[starts-with(@class, 'Todos__innerFeedContainer')]"))
        )

        #print("[INFO] Assignments container loaded successfully")

        time.sleep(1)

        assignments = []
        assignments_num = int(driver.find_element(By.XPATH, "//div[. = 'Upcoming']/following-sibling::div").text)

        #print(f"[INFO] {assignments_num} assignments found")

        while len(assignments) < assignments_num:
            assignments = driver.find_elements(By.XPATH, "//*[starts-with(@class, 'FeedItem__container')]")
            #print(f"[INFO] Scrolling to load more assignments... {len(assignments)}/{assignments_num} assignments loaded")
            driver.execute_script("arguments[0].scrollIntoView();", assignments[-1])
            time.sleep(0.5)
        
        #print("[INFO] All assignments loaded successfully")
        return assignments, assignments_num



    url = "https://web.toddleapp.com/platform?type=loginForm&usertype=student"
    driver.get(url)

    username_input = driver.find_element(By.XPATH, '//input[@name="email"]')
    password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
    submit_button = driver.find_element(By.XPATH, "//button[@data-test-id='button-sign-in-button']")

    username_input.send_keys(MyUsername)
    password_input.send_keys(MyPassword)
    submit_button.click()

    try:
        WebDriverWait(driver, 5).until( # Check if logged in
            EC.presence_of_element_located((By.XPATH, "//*[starts-with(@class, 'Todos__innerFeedContainer')]"))
        )
    except:
        print(f"[WARNING] {MyUsername} credentials incorrect.")
        return

    time.sleep(2)

    while True:
        driver.get("https://web.toddleapp.com/platform/3716/todos")
        assignments, assignments_num = load_all_assignments()
        assingment_data = []
    
        for assignment in assignments:
            name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[1]').text
            class_name = assignment.find_element(By.XPATH, './div[1]/div/div[2]/div[2]').text
            due_date = assignment.text.strip().split('Due on')[1].split('Status')[0].strip()
            #print(f"[INFO] Scraped assignment: {name} - {class_name} - {due_date}")
            assingment_data.append(tuple((name, class_name, due_date)))

        if '' in [assignment[2] for assignment in assingment_data]:
            if failcount == 5:
                #print("[WARNING] Due date missing more than 5 times, skipping...")
                break
            #print("[WARNING] Some assignments have no due date, retrying...")
            #print("[WARNING] Missing dates: ", [assignment for assignment in assingment_data if assignment[2] == ''])
            assingment_data = []
            failcount += 1
        else:
            break

    for i in range(assignments_num):
        #print(f"[INFO] Scraping link for assignment {i + 1}/{assignments_num}...")
        if assingment_data[i][2] == '':
            pass
        actions.move_to_element(assignments[i]).click().perform()
        link = driver.current_url
        assingment_data[i] = assingment_data[i] + (link,)
        driver.back()
        assignments, _ = load_all_assignments()
        time.sleep(1)

    test = []

    for assignment in assingment_data:
        if assignment[2] != '':
            test.append(assignment)

    assingment_data = test
    
    
    def convert_date(input_date):
        without_day = input_date[input_date.find(',') + 1:].strip()
        if input_date[:input_date.find(',')].strip() == 'Tomorrow':
            date = datetime.today() + timedelta(days=1)
            date = date.strftime("%d %b %Y")
            time = without_day
        elif input_date[:input_date.find(',')].strip() == 'Today':
            date = datetime.today().strftime("%d %b %Y")
            time = without_day
        else:
            date = without_day[:without_day.find(',')]
            time = without_day[without_day.find(',') + 1:].strip()
        date_formatted = datetime.strptime(date, "%d %b %Y").strftime("%Y-%m-%d")
        if ":" in time:
            time_formatted = datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")
        else:
            time_formatted = datetime.strptime(time, "%I %p").strftime("%H:%M:%S")
        return f"{date_formatted} {time_formatted}"

    c = Calendar()

    #print([assignment[2] for assignment in assingment_data])

    for assignment in assingment_data:
        e = Event()
        e.name = assignment[0]
        e.description = assignment[1] + "\n" + '<a href="' + assignment[3] + '">Link</a>'
        e.begin = e.end = convert_date(assignment[2])
        e.url = assignment[3]
        c.events.add(e)
    
    filename = MyUsername.split("@")[0] + ".ics"
    with open(filename, 'w') as my_file:
        my_file.writelines(c.serialize_iter())

    print(f"[INFO] Succesfully scraped {MyUsername}.")

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
    print("[INFO] Scraping " + username + "'s toddle...")
    scrape_toddle(username, password)
