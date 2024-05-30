from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller  # setup chrome options
import requests

import sys
import os
import re
import time
import pandas as pd

search_query = 'AI'
download_path = 'C:\\Users\\82106\\OneDrive\\바탕 화면\\project\\opensource\\images\\' + f'{search_query}'
MAX_IMAGES = 10

# wait time
SEARCH_TIME = 0.5
WAIT_TIME = 2
SCROLL_PAUSE_TIME = 5

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-popup-blocking") # 팝업창 차단 설정
chrome_options.add_argument("--disable-notifications") # 알림 요청 차단
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("--headless")  # headless 모드 설정
# chrome_options.add_argument("--window-size=1920x1080")  # headless 모드에서 창 크기 설정

# ChromeDriver 자동 설치 및 경로 가져오기
chrome_driver_path = chromedriver_autoinstaller.install()

# Service 객체 생성
service = Service(chrome_driver_path)

# 크롬 드라이버에 옵션 적용
driver = webdriver.Chrome(service=service, options=chrome_options)

# Google URL
url = 'https://www.google.com/'

# Driver setting
driver.get(url)

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
images_collected = 0  # 수집된 이미지 개수 카운팅을 위한 변수
url_list = []
last_height = driver.execute_script("return document.body.scrollHeight")

while images_collected < MAX_IMAGES:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

    # 클래스명이 'EZAeBe'인 모든 <a> 태그를 찾음
    links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.EZAeBe"))
    )

    for link in links:
        try:

            # <img> 태그 수집
            img = link.find_element(By.TAG_NAME, 'img')
            img_url = img.get_attribute('src')

            if img_url and img_url.startswith('http'):
                images_collected += 1

                # 사이트 URL 수집
                site_url = link.get_attribute('href')
                url_list.append(site_url)

                print(f'{images_collected}/{MAX_IMAGES} | 이미지 URL: {img_url}, 사이트 URL: {site_url}')
                
                if images_collected >= MAX_IMAGES:
                    break
        except Exception as e:
            print(f'오류 발생: {e}')

    if images_collected >= MAX_IMAGES:
        break

# 마지막으로 한 번 더 이미지를 수집하여 확인
images_area = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.YQ4gaf"))
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

# URL 리스트를 CSV 파일로 저장
image_num = [f'{search_query}_{num}' for num in range(1, images_collected + 1)]
url_df = pd.DataFrame({'image_name': image_num, 'URL': url_list})
url_df.to_csv(os.path.join(download_path, 'image_url.csv'), index=False)

end_time = time.time()
print('Loading time:', end_time - start_time, 'seconds')

# 드라이버 종료
driver.close()