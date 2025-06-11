import csv
import json
import sys
from time import sleep
import time
import traceback
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium import webdriver

from seleniumbase import Driver
sys.stderr = open('selenium-error.log', 'w')

class tw_ifoodie_page_extractor():
    def __init__(self):
        def get_processed_notes():
            processed_notes = []
            # 開啟CSV檔案進行讀取
            with open('note.csv', 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                
                # 跳過標題行
                next(csv_reader)
                
                # 遍歷每一行數據
                for row in csv_reader:
                    processed_notes.append(row[0])
            return processed_notes
        #self.browser_executable_path = ""
        #download_undetected_chromedriver(self.browser_executable_path, undetected=True, arm=False, force_update=True)
        #self.browser_executable_path = os.path.abspath("chromedriver.exe")
        
        #self.driver = uc.Chrome(options=get_ChromeOptions(), executable_path=self.browser_executable_path, version_main=110)
        self.driver = Driver(uc=True, headless=False, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36")
        self.wait = WebDriverWait(self.driver, 10, poll_frequency=1, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        
        procressed_notes = get_processed_notes()
        self.data = self.load_data_csv()
        for item in self.data:
            if item[0] not in procressed_notes:
                
                self.extract_note(item)
            
        
        self.driver.close()
    def load_data_csv(self, csv_file='processed_data.csv'):
        out = []
        count = 0
        with open(csv_file, 'r', encoding="utf-8") as file:
            # 創建一個csv讀取器對象
            csv_reader = csv.reader(file)
            
            # 遍歷讀取器對象，每次讀取一行數據
            for row in csv_reader:
                if count != 0:        
                    # row變數是一個列表，包含該行的所有數據
                    out.append(row)
                count += 1
        return out
     
    def extract_page(self, item):
        print(item[2])
        page = item[2]
        self.driver.get(page)
        
        time.sleep(1)
        #self.driver.execute_script("window.stop()")
        self.driver.switch_to.default_content()
    def extract_note(self, item):
        if(item[3] == ""):
            #此餐廳沒有文章
            return
        print(item[3])
        self.driver.get(item[3])
        time.sleep(1)
        try:
            readmore = self.driver.find_element(By.XPATH, "//a[@class='readmore']")
        except:
            return 0
        link = readmore.get_attribute('href')
        self.driver.execute_script("arguments[0].click();", readmore)
        time.sleep(1)
        ps = self.driver.find_elements(By.XPATH, "//p")
        note = ""
        for p in ps:
            note += p.text.replace("\n", " ")
        
        with open("note.csv", mode='a', encoding='utf-8', newline='') as csv_file:
            fieldnames = ["restaurant_title", "restaurant_note"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # Check if the file is empty, if so, write the header
            csv_file.seek(0, 2)  # Move to the end of file
            if csv_file.tell() == 0:  # Check file position
                writer.writeheader()
            
            data = {
                "restaurant_title": item[0],
                "restaurant_note": note
            }
            writer.writerow(data)

crawler = tw_ifoodie_page_extractor()
