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


chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

# 사용자 입력 : 검색어 & 저장 경로
search_query = 'python'
download_path = './image'

# 이미지를 저장할 폴더 생성(없을 경우)
if not os.path.exists(download_path):
    os.makedirs(download_path)

# google url
url = 'https://www.google.com/'

# driver setting
driver.get(url)

# 검색어 입력 및 제출
element = driver.find_element(By.NAME,'q')
element.send_keys(search_query)
element.submit()
time.sleep(0.5)  

# '이미지' 탭으로 이동
images_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
)
images_tab.click()

# 스크롤 다운
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  

# parser 생성
web = driver.page_source
source = BeautifulSoup(web, 'html.parser')

# 이미지 URL 수집
image_elements = source.find_all('img', {'class':'YQ4gaf'})
image_urls = set()
for img in image_elements[:50]:
    src = img.get('src') or img.get('data-src')  # 'src' 또는 'data-src' 속성에서 URL 가져옴
    if src:
        image_urls.add(src)

for i, url in enumerate(image_urls):
    try:
        response = requests.get(url)
        with open(os.path.join(download_path, f'image_{i}.jpg'), 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading {url}: {e}")

driver.quit()
print("이미지 다운로드 완료")