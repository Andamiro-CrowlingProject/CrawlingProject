from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import sys
import os
import re
import time

# Headless 모두를 위한 옵션 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-setuid-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option('excludeSwitches',['enable-logging'])

# 브라우저 환경을 통해 크롬드라이버 환경을 자동으로 설정
driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = chrome_options)

# 사용자 입력을 통해 검색어 및 저장 경로 설정
search_word = input("Please enter your search word: ")
download_path = f'./image/{search_word}'

# 이미지를 저장할 디렉토리가 없을 경우 생성
if not os.path.exists(download_path):
    os.makedirs(download_path)

# google url 설정
url = 'https://www.google.com/'

# driver 설정
driver.get(url)

# 검색어 입력 및 제출
search_bar = driver.find_element(By.NAME,'q')
search_bar.send_keys(search_word)
search_bar.submit()
time.sleep(1)  

# '이미지' 탭으로 이동
images_tab = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
)
images_tab.click()

# 스크롤 다운을 통한 이미지 로딩 개선
scroll_pause_time = 2  # 스크롤 사이의 대기 시간
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 이미지 URL 수집
web = driver.page_source
source = BeautifulSoup(web, 'html.parser')
image_elements = source.find_all('img', {'class':'YQ4gaf'})
image_urls = set()
for img in image_elements:
    src = img.get('src') or img.get('data-src')  # 'src' 또는 'data-src' 속성에서 URL 가져옴
    if src:
        image_urls.add(src)

# 이미지 다운로드
for i, url in enumerate(image_urls):
    try:
        response = requests.get(url)
        with open(os.path.join(download_path, f'{search_word}_{i}.jpg'), 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error downloading {url}: {e}")

driver.quit()
print("done")