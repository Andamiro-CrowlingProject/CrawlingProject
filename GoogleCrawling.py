from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller  # setup chrome options
import requests

import traceback

import sys
import os
import re
import time
import pandas as pd

def setup_crawling():
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
    
    return driver

def crawl_images(driver, search_query, max_images, search_time=0.5, wait_time=2, scroll_pause_time=5):
    # Google URL
    url = 'https://www.google.com/'

    # Driver setting
    driver.get(url)

    # 검색어 입력 및 제출
    element = driver.find_element(By.NAME, 'q')
    element.send_keys(search_query)
    element.submit()
    time.sleep(search_time)

    # '이미지' 탭으로 이동
    try:
        images_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
        )
        images_tab.click()
    except:
        try:
            images_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(By.LINK_TEXT, 'Images')
            )
            images_tab.click()
        except:
            print("'이미지' 탭을 찾을 수 없습니다.")
            driver.quit()
            return []

    time.sleep(wait_time)

    # 필요한 변수 초기화
    images_collected = 0
    url_list = []

    while images_collected < max_images:
        try:
            # 이미지 큰 범위 선택
            image_area = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.H8Rx8c'))
            )
            print(image_area)
            
            for image_contents in image_area:
                try:
                    # 요소가 화면에 나타나도록 스크롤
                    driver.execute_script("arguments[0].scrollIntoView();", image_contents)
                    time.sleep(1)  # 잠시 대기

                    # 요소 클릭 시도
                    image_contents.click()
                    print(f"Clicked on: {image_contents}")

                    try:
                        # src 요소 수집
                        src_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.sFlh5c.pT0Scc.iPVvYb'))
                        )
                        print('Read the src')

                        # href 요소 수집
                        atag_href_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.umNKYc'))
                        )
                        if atag_href_elements:
                            href_element = atag_href_elements[0].get_attribute('href')
                            print(f"href: {href_element}")
                        else:
                            href_element = None

                        # 각 src 요소의 src 속성 값 / href 요소의 href 속성 값을 추출하여 리스트에 추가
                        for src_element in src_elements:
                            src_value = src_element.get_attribute('src')
                            print(f"src: {src_value}")

                            url_list.append((src_value, href_element))

                        images_collected += len(src_elements)
                        if images_collected >= max_images:
                            break

                    except TimeoutException as e:
                        print("[ Error type ] Timeout while waiting for elements")
                        print(e)
                        continue  # 다음 이미지 탭으로 이동

                except ElementClickInterceptedException as e:
                    print("[ Error type ] ElementClickInterceptedException")
                    print(e)
                    continue  # 다음 이미지 탭으로 이동

        except Exception as e:
            print("[ Error type ] General Exception")
            print(e)
            traceback.print_exc()

    # 브라우저 종료
    driver.quit()
    return url_list

def save_images(search_query, download_path, url_list, max_images):
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

    # 이미지 다운로드 및 저장
    count = 1
    for imgUrl, siteUrl in url_list:
        try:
            img_data = requests.get(imgUrl).content

            # URL에서 확장자 추출
            _, ext = os.path.splitext(imgUrl)

            # 확장자가 유효하지 않거나 없는 경우 기본적으로 .jpg로 설정
            if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
                ext = '.jpg'

            # 이미지 저장 경로 설정
            image_path = os.path.join(download_path, f"{search_query}_{count}{ext}")

            with open(image_path, 'wb') as handler:
                handler.write(img_data)
            print(f"Image saved: {search_query}_{count}{ext}")
            count += 1
            if count > max_images:
                break
        except Exception as e:
            print(f"Failed to save image {count}: {e}")

    # URL 리스트를 CSV 파일로 저장
    image_num = [f'{search_query}_{num}' for num in range(1, count)]
    url_df = pd.DataFrame({'image_name': image_num, 'imgUrl': [url[0] for url in url_list[:count-1]], 'siteUrl': [url[1] for url in url_list[:count-1]]})
    url_df.to_csv(os.path.join(download_path, 'image_url.csv'), index=False)
    print("CSV file saved: image_url.csv")


def find_duplicates(download_path):
    # 이미지 파일 읽기
    images = [file for file in os.listdir(download_path) if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'))]
    image_paths = [os.path.join(download_path, img) for img in images]

    # ORB 디텍터 생성
    orb = cv2.ORB_create()

    # 이미지별로 특징점과 기술자 추출
    descriptors = []
    for image_path in image_paths:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, des = orb.detectAndCompute(img, None)
        descriptors.append(des)

    # 모든 이미지 쌍에 대해 유사도 계산
    duplicates = []
    for (img1, des1), (img2, des2) in combinations(zip(image_paths, descriptors), 2):
        # BFMatcher : 전수 조사 매칭(객체 인식&추적)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        
        # 유사도는 매칭된 특징점의 수로 결정
        similarity = len(matches)

        # 유사도가 특정 임계값 이상이면 중복으로 간주
        if similarity > 1:  
            duplicates.append((img1, img2))

    return duplicates


duplicates = find_duplicates(download_path)

if duplicates:
    for dup in duplicates:
        print(f"중복된 이미지: {dup[0]} and {dup[1]}")
else:
    print("중복된 이미지가 없습니다.")