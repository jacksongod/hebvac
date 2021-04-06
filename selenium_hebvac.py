from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException,TimeoutException,ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from subprocess import Popen,PIPE
import os, sys
import random
import time
import atexit
import yaml



timeout_value=10
script_dir_path = os.path.dirname(os.path.realpath(__file__))

def make_exit_handler(phone, disable):
    def exit_handler():
        Hebvac.send_imessage (phone, 'Script hit uncaught exception and ended',disable=disable)
    return exit_handler


class Hebvac:
    def __init__(self,config_dict,driver):
        self.driver = driver
        self.phone = config_dict['phone']
        self.use_imessage = config_dict['use_imessage']
        atexit.register(make_exit_handler(self.phone, not self.use_imessage))
        self.location_list = [x+', TX' for x in config_dict['city_list']]
        self.use_city = config_dict['use_city']
        self.type_list = config_dict['type_list']
        self.use_type = config_dict['use_type']
        self.max_distance = config_dict['max_distance']
        self.use_distance = config_dict['use_distance']
        # self.my_zipcode = config_dict['my_zipcode']

    @staticmethod
    def send_imessage(phone_list, body,disable=False):
        if disable:
            return 
        for phonenumber in phone_list:
            Popen(['osascript',os.path.join(script_dir_path,'iMessage.scpt'),phonenumber, body],stdout=sys.stdout,stderr=sys.stderr)


    def check_exists_by_css(self, dr, css_sel):
        try:
            dr.find_element_by_css_selector(css_sel)
        except NoSuchElementException:
            return False
        return True


    def click_time_page(self, title, address, distance):
        try:
            WebDriverWait(self.driver,timeout_value/2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown-element-14"]')))
        except TimeoutException:
            print (f'Enter time page failed')
            return None 
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        find_date_list = self.driver.find_elements_by_xpath('//*[@id="dropdown-element-14"]')
        # find_date_list= WebDriverWait(self.driver, 5).until(lambda s: s.find_element_by_id('dropdown-element-14'))
        find_time_list = self.driver.find_elements_by_xpath('//*[@id="dropdown-element-18"]')

        if not find_date_list or not find_time_list:
            print ("not find drop down 14 and 18")
            # time.sleep(300)
            return None

        self.driver.find_element_by_xpath('//*[@id="input-14"]').click()
        try:
            find_date_list[0].find_element_by_css_selector("lightning-base-combobox-item:nth-child(1)").click()
        except :
            print (f'no time slot for {title}')
            return None
        selected_date = find_date_list[0].find_element_by_xpath('//*[@id="input-14-0-14"]/span[2]/span').get_attribute("title")
        print(selected_date)
        time.sleep(0.3)
        self.driver.find_element_by_xpath('//*[@id="input-18"]').click()
        find_time_list[0].find_element_by_css_selector("lightning-base-combobox-item:nth-child(1)").click()
        selected_time = find_time_list[0].find_element_by_xpath('//*[@id="input-18-0-18"]/span[2]/span').get_attribute("title")
        print(selected_time)
        time.sleep(0.2)
        try:
            driver.find_element_by_xpath('//*[@id="container"]/c-f-s-registration/div/div[1]/div[4]/lightning-button/button').click()
        except ElementClickInterceptedException:
            print (f'click intercepted  {title}')
            return None 
        try:
            WebDriverWait(self.driver, timeout_value).until(lambda s: s.find_element_by_xpath('//*[@id="container"]/c-f-s-registration/div/div[1]/div[2]/div/div/p')) 
        except TimeoutException:
            print (f'submit failed for {title}')
            return None 

        Hebvac.send_imessage(self.phone, f'Found {distance} miles {title} {selected_date} {selected_time} {address}. You have 10 mins',disable = not self.use_imessage)
        time.sleep(1200)

    def in_list_of_location (self, element , location_list):
        address = element.find_element_by_css_selector('div address').text
        return any(x in address for x in location_list)

    def in_list_of_type (self,element , type_list):
        try:
            vac_type = element.find_element_by_css_selector('div p.jzOQjz').text
            return any(x in vac_type for x in type_list) 
        except:
            return False

    def in_distance (self, element , max_distance):
        try:
            distance_string = element.find_element_by_css_selector('p.evtGGn').text.split(' ')[0]
            distance = float(distance_string)
            return max_distance > distance
        except:
            return False

    def processing(self):
            # time.sleep(3)
        while True:
            sleep_time = random.randint(0, 50)/10
            myElem = WebDriverWait(self.driver,timeout_value).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[3]/div[2]/div/button')))
            print (myElem.text)
            myElem.click()
            WebDriverWait(self.driver, timeout_value).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#root > div.sc-kstrdz.khymNb > div.sc-bdfBwQ.sc-bkzZxe.iXgbQJ.dHUsHE > div.sc-bdfBwQ.sc-hBEYos.iXgbQJ.gBMEYn > div > button")))
            table_list= self.driver.find_elements_by_css_selector('.sc-fFubgz > li.sc-iBPRYJ')
            print (f'{len(table_list)} available Locations')
            table_list = [ x for x in table_list if 
                                                    (not self.use_city or self.in_list_of_location(x, self.location_list)) and  
                                                    (not self.use_type or self.in_list_of_type(x, self.type_list)) and  
                                                    (not self.use_distance or self.in_distance (x, self.max_distance)) and 
                                                    (self.check_exists_by_css(x,'div p.lhuWlB') or self.check_exists_by_css(x,'div p.ekqPWg'))]

            print (f'{len(table_list)} filtered available Locations')
            if not table_list:
                # sleep_time = random.randint(0, 8)
                print (f'Sleep for {sleep_time}s...')
                time.sleep(sleep_time)   
                continue
            # print (f'{len(table_list)} places found')
            # for a in table_list:
            selected = random.choice(table_list)
            # a = table_list[0]
            title = selected.find_element_by_css_selector('div:nth-child(1) p.sc-gsTCUz.bJtRjk').text
            address = selected.find_element_by_css_selector('div address').text
            # link= a.find_element_by_css_selector('div.kjxcKy a').get_attribute('href')
            # vac_type = a.find_element_by_css_selector('div:nth-child(1) p.jzOQjz').text
            try:
                distance_string = selected.find_element_by_css_selector('p.evtGGn').text
                distance = distance_string.split(' ')[0]
            except :
                distance = 'unknown'
            selected.find_element_by_css_selector('div.kjxcKy a').click()

            print (distance)
            # time.sleep(2.2)
            self.click_time_page(title,address, distance)
            print (f'not find in the page  {title}')
            self.driver.back()

            print (f'Sleep for {sleep_time}s...')
            time.sleep(sleep_time)   
            # self.driver.refresh()

if __name__ == '__main__':
    
    with open(os.path.join(script_dir_path,'config.yml')) as file :
        config_dict = yaml.load(file,Loader=yaml.FullLoader)
    # location_key = ['TX']
    chrome_options = webdriver.ChromeOptions()
    # Add the mobile emulation to the chrome options variable
    mobile_emulation = { 
        "deviceName": "iPhone X"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    # For older ChromeDriver under version 79.0.3945.16
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    #For ChromeDriver version 79.0.3945.16 or over
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(config_dict['chrome_driver_path'], options=chrome_options) 
    #Remove navigator.webdriver Flag using JavaScript
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get('https://vaccine.heb.com/scheduler?q='+str(config_dict['my_zipcode']))
    # driver.get('https://vaccine.heb.com/scheduler')


    hebvac = Hebvac(config_dict,driver)
    hebvac.processing()