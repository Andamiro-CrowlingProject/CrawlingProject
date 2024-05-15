from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller  # setup chrome options
from bs4 import BeautifulSoup
import requests

import sys
import os
import re
import time
import pandas as pd


# 사용자 입력: 검색어 & 저장 경로 & Maximum 이미지 개수
search_query = 'AI'
download_path = 'C:\\Users\\82106\\OneDrive\\바탕 화면\\project\\opensource\\images\\' + f'{search_query}'
MAX_IMAGES = 50

# wait time
SEARCH_TIME = 0.5
WAIT_TIME = 1
SCROLL_PAUSE_TIME = 1

# ChromeDriver 자동 설치
chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

start_time = time.time()
# 이미지를 저장할 폴더 생성(없을 경우)
if not os.path.exists(download_path):
    os.makedirs(download_path)
else:
    # 폴더가 이미 존재하면 폴더 내의 모든 파일 삭제
    for file_name in os.listdir(download_path):
        file_path = os.path.join(download_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

# Google URL
url = 'https://www.google.com/'

# Driver setting
driver.get(url)

# 검색어 입력 및 제출
element = driver.find_element(By.NAME, 'q')
element.send_keys(search_query)
element.submit()
time.sleep(SEARCH_TIME)  

# '이미지' 탭으로 이동
images_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
)
images_tab.click() 

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(WAIT_TIME)

# 이미지 URL 수집
images_collected = 0 # 수집된 이미지 개수 카운팅을 위한 변수

while images_collected < MAX_IMAGES + 10:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")

    images_area = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.Q4LuWd"))
    )

    for image in images_area[images_collected:]:
        try:
            imgUrl = image.get_attribute('src')
            if imgUrl.startswith('http'):
                images_collected += 1
                if images_collected >= MAX_IMAGES:
                    break
        except Exception as e:
            print(e)

    if images_collected >= MAX_IMAGES:
        break

    last_height = new_height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break

images_area = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.Q4LuWd"))
)

count = 1
for image in images_area:
    try:
        imgUrl = image.get_attribute('src')
        if imgUrl.startswith('http') and count <= MAX_IMAGES:
            img_data = requests.get(imgUrl).content
            with open(os.path.join(download_path, f"{search_query}_{count}.jpg"), 'wb') as handler:
                handler.write(img_data)
            print(f"Image saved: {search_query}_{count}.jpg")
            count += 1
        if count > MAX_IMAGES:
            break
    except Exception as e:
        print(e)

end_time = time.time()
print('Loading time:',end_time - start_time,'second')

driver.close()