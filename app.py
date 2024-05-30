from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import requests

import os
import time
import pandas as pd

def setup_driver():
    # 크롬 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-popup-blocking")  # 팝업창 차단 설정
    chrome_options.add_argument("--disable-notifications")  # 알림 요청 차단
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")  # headless 모드 설정
    chrome_options.add_argument("--window-size=1920x1080")  # headless 모드에서 창 크기 설정

    # ChromeDriver 자동 설치 및 경로 가져오기
    chrome_driver_path = chromedriver_autoinstaller.install()

    # Service 객체 생성
    service = Service(chrome_driver_path)

    # 크롬 드라이버에 옵션 적용
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def GoogleCrawling(search_query, download_path, MAX_IMAGES=10):
    driver = setup_driver()

    # Google 홈페이지로 이동
    driver.get('https://www.google.com/')

    start_time = time.time()
    # 이미지를 저장할 폴더 생성(없을 경우)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    else:
        # 폴더가 이미 존재하면 폴더 내의 모든 파일 삭제
        print('기존의 파일 삭제 후 작업 시행합니다.')
        for file_name in os.listdir(download_path):
            file_path = os.path.join(download_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # 검색어 입력 및 제출
    element = driver.find_element(By.NAME, 'q')
    element.send_keys(search_query)
    element.submit()
    time.sleep(0.5)

    # '이미지' 탭으로 이동
    images_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
    )
    images_tab.click()
    time.sleep(2)

    images_collected = 0
    url_list = []

    while images_collected < MAX_IMAGES:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.EZAeBe"))
        )

        for link in links:
            try:
                img = link.find_element(By.TAG_NAME, 'img')
                img_url = img.get_attribute('src')

                if img_url and img_url.startswith('http'):
                    images_collected += 1

                    site_url = link.get_attribute('href')
                    url_list.append(site_url)

                    print(f'{images_collected}/{MAX_IMAGES} | 이미지 URL: {img_url}, 사이트 URL: {site_url}')
                    
                    if images_collected >= MAX_IMAGES:
                        break
            except Exception as e:
                print(f'오류 발생: {e}')

        if images_collected >= MAX_IMAGES:
            break

    count = 1
    for imgUrl, siteUrl in zip(url_list, url_list):
        try:
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

    driver.quit()

if __name__ == '__main__':
    search_query = 'AI'
    download_path = 'C:\\Users\\82106\\OneDrive\\바탕 화면\\project\\opensource\\images\\' + f'{search_query}'
    MAX_IMAGES = 10

    GoogleCrawling(search_query, download_path, MAX_IMAGES)