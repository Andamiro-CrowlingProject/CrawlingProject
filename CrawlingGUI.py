import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QApplication, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller  # setup chrome options
import requests


import cv2
# from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
# from tensorflow.keras.preprocessing import image
# from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations
from PIL import Image 
import os
from itertools import combinations

import sys
import os
import time
import pandas as pd
import numpy as np
import base64


class GoogleCrawling:
    """
    Google 이미지를 크롤링하는 클래스입니다.

    메서드:
    setup_crawling():
        크롬 드라이버를 설정하고 반환합니다.

    crawl_images(search_query, max_images=10, wait_time=2):
        주어진 검색어로 이미지를 크롤링하여 URL 리스트를 반환합니다.

    save_images(self, search_query, download_path, url_list, max_images):
        이미지를 다운로드하고 저장합니다.

    find_duplicates(self, download_path, similarity_threshold=30):    
        중복이미지를 검출합니다.
    """

    def __init__(self, search_query, max_images, download_path):
        """
        GoogleCrawling 클래스의 인스턴스를 초기화합니다.

        Args:
        search_query (str): 검색어.
        max_images (int): 다운로드할 최대 이미지 수.
        download_path (str): 다운로드할 경로.
        """
        self.search_query = search_query
        self.max_images = max_images
        self.download_path = download_path
        self.url = 'https://www.google.com/'


    def setup_crawling(self):
        """
        크롬 드라이버를 설정하고 반환합니다.
        """
        chrome_options = Options()
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")

        chrome_driver_path = chromedriver_autoinstaller.install()
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver


    def crawl_images(self, search_query, max_images=10, wait_time=2):
        """
        주어진 검색어로 이미지를 크롤링하여 URL 리스트를 반환합니다.

        Args:
        search_query (str): 검색어.
        max_images (int): 다운로드할 최대 이미지 수. 기본값은 10.
        wait_time (int): 대기 시간(초). 기본값은 2초.
        scroll_pause_time (int): 스크롤 후 대기 시간(초). 기본값은 5초.
        """
        driver = self.setup_crawling()
        driver.get(self.url)

        element = driver.find_element(By.NAME, 'q')
        element.send_keys(search_query)
        element.submit()
        time.sleep(wait_time)

        # '이미지' 탭 클릭
        try:
            images_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, '이미지'))
            )
            images_tab.click()
        except:
            try:
                images_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, 'Images'))
                )
                images_tab.click()
            except:
                print("'이미지' 탭을 찾을 수 없습니다.")
                driver.quit()
                return []

        time.sleep(wait_time)

        images_collected = 0
        url_list = []

        while images_collected < max_images:
            try:
                image_area = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.H8Rx8c'))
                )
                
                for image_contents in image_area:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView();", image_contents)
                        time.sleep(1)
                        image_contents.click()

                        try:
                            # 이미지 src 수집
                            src_elements = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.sFlh5c.pT0Scc.iPVvYb'))
                            )
                            
                            # 이미지 href 수집
                            atag_href_elements = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.umNKYc'))
                            )
                            href_element = atag_href_elements[0].get_attribute('href') if atag_href_elements else None

                            # src, href 매핑
                            for src_element in src_elements:
                                src_value = src_element.get_attribute('src')
                                url_list.append((src_value, href_element))

                            images_collected += len(src_elements)
                            if images_collected >= max_images:
                                break

                        except TimeoutException as e:
                            print("[ Error type ] Timeout while waiting for elements")
                            print(e)
                            continue

                    except ElementClickInterceptedException as e:
                        print("[ Error type ] ElementClickInterceptedException")
                        print(e)
                        continue

            except Exception as e:
                print("[ Error type ] General Exception")
                print(e)

        driver.quit()
        return url_list


    def save_images(self, search_query, download_path, url_list, max_images):
        """
        이미지를 다운로드하고 저장합니다.
        
        Args:
            search_query (str): 검색 쿼리.
            download_path (str): 이미지를 저장할 경로.
            url_list (list): 이미지 URL 및 사이트 URL 리스트.
            max_images (int): 다운로드할 최대 이미지 수.
        """
        # search_query 폴더가 없으면 생성, 있으면 모든 파일 삭제
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        else:
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
            except requests.exceptions.RequestException as e:
                print(f"Failed to save image {count}: {e}")

        # URL 리스트를 CSV 파일로 저장
        image_num = [f'{search_query}_{num}' for num in range(1, count)]
        url_df = pd.DataFrame({
            'image_name': image_num,
            'imgUrl': [url[0] for url in url_list[:count-1]],
            'siteUrl': [url[1] for url in url_list[:count-1]]
        })
        url_df.to_csv(os.path.join(download_path, 'image_url.csv'), encoding='utf-8-sig', index=False)
        print("CSV file saved: image_url.csv")


    def find_duplicates(self, download_path, similarity_threshold=30):
        """
        중복 이미지를 검출합니다.
        
        Args:
            download_path (str): 이미지를 저장한 경로.
            similarity_threshold (int): 유사도 임계값.
        """
        print("중복 이미지 검출 중입니다.")
    
        
        # 이미지 파일 읽기
        images = [file for file in os.listdir(download_path) if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'))]
        image_paths = [os.path.join(download_path, img) for img in images]

        # ORB 디텍터 생성
        orb = cv2.ORB_create()

        # 이미지별로 특징점과 기술자 추출
        descriptors = []
        for image_path in image_paths:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                # print(f"이미지를 읽을 수 없습니다: {image_path}")
                continue
            _, des = orb.detectAndCompute(img, None)
            descriptors.append((image_path, des))

        # 모든 이미지 쌍에 대해 유사도 계산
        duplicates = []
        for (img1, des1), (img2, des2) in combinations(descriptors, 2):
            if des1 is None or des2 is None:
                continue
            
            # BFMatcher : 전수 조사 매칭(객체 인식&추적)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            
            # 유사도는 매칭된 특징점의 수로 결정
            similarity = len(matches)

            # 유사도가 특정 임계값 이상이면 중복으로 간주
            if similarity > similarity_threshold:  
                duplicates.append((img1, img2))

        if duplicates:
            for dup in duplicates:
                print(f"중복된 이미지: {dup[0]} and {dup[1]}")
        else:
            print("중복된 이미지가 없습니다.")


class MyApp(QWidget):
    """
    MyApp 클래스는 PyQt5를 사용하여 GUI를 생성합니다. 사용자는 검색어, 이미지 개수, 저장 경로를 입력하고
    '검색' 버튼을 클릭하여 이미지를 크롤링하고 저장할 수 있습니다.
    """
    
    def __init__(self):
        """
        MyApp 클래스의 생성자입니다. 초기화 메서드를 호출하여 UI를 설정합니다.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        UI를 초기화하고 위젯들을 배치합니다.
        """
        self.resize(500, 350)
        self.center()
        
        layout = QVBoxLayout()
        
        self.le_search = QLineEdit(self)
        self.le_search.setPlaceholderText('검색어를 입력해주세요.')
        
        self.le_num = QLineEdit(self)
        self.le_num.setPlaceholderText('수집할 이미지의 개수를 입력해주세요.')
        
        self.le_path = QLineEdit(self)
        self.le_path.setPlaceholderText('저장 경로를 지정해주세요.')
        
        self.btn_search = QPushButton('검색', self)
        self.btn_search.clicked.connect(self.start_crawling)
        
        self.lbl_link = QLabel(self)
        self.lbl_link.setOpenExternalLinks(True)  # 하이퍼링크를 클릭할 수 있도록 설정

        # 선 추가 함수
        def add_line():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addWidget(line)

        # 폼 구성
        layout.addStretch(1)  # 가변적인 공간 추가     
        layout.addWidget(self.le_search)
        layout.addStretch(1)  # 가변적인 공간 추가        
        layout.addWidget(self.le_num)
        layout.addStretch(1)  # 가변적인 공간 추가
        layout.addWidget(self.le_path)
        layout.addStretch(1)  # 가변적인 공간 추가
        layout.addWidget(self.btn_search)
        add_line()
        layout.addWidget(self.lbl_link)  # QLabel을 레이아웃에 추가
        
        self.setLayout(layout)
        
        self.show()
    
    def center(self):
        """
        창을 화면의 중앙에 배치합니다.
        """
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_crawling(self):
        """
        '검색' 버튼 클릭 시 호출됩니다. 입력된 값을 읽고 이미지를 크롤링하여 저장합니다.
        """
        search_query = self.le_search.text()
        try:
            max_images = int(self.le_num.text())
        except ValueError:
            QMessageBox.warning(self, '입력 오류', '이미지 개수는 숫자로 입력해주세요.')
            return
        path = self.le_path.text() + '\\CrawlingImage\\' 
        download_path = path + f'{search_query}'

        # 크롤링
        try:
            GC = GoogleCrawling(search_query, max_images, download_path)
            url_list = GC.crawl_images(search_query, max_images)  # 크롤링
            GC.save_images(search_query, download_path, url_list, max_images)  # 이미지 저장
            GC.find_duplicates(download_path)  # 중복찾기
        except Exception as e:
            QMessageBox.critical(self, '오류', f'오류가 발생했습니다: {e}')
            return

        if url_list:
            QMessageBox.information(self, '완료', f'총 {len(url_list)}개의 이미지를 수집했습니다.')
            # 저장된 경로로 이동할 수 있는 하이퍼링크 설정
            self.lbl_link.setText(f'<a href="file:///{download_path}">저장된 이미지 폴더 열기</a>')
        else:
            QMessageBox.warning(self, '실패', '이미지 수집에 실패했습니다.')
            self.lbl_link.clear()  # 실패 시 하이퍼링크 제거



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())