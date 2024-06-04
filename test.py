from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import os
import time
import urllib.request
import pandas as pd

def setup_driver():
    # Headless 모드를 위한 옵션 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # USer-Agent 설정
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    # chrome_options.add_argument(f'user-agent = {user_agent}')

    # 크롤링을 위한 ChromeDriver 자동 설치
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def create_dir(search_word):
    # 사용자 입력을 통해 검색어 및 저장 경로 설정
    download_path = f'./images/{search_word}'
    download_urls_path = f'./urls/{search_word}'

    os.makedirs(download_path, exist_ok=True)
    os.makedirs(download_urls_path, exist_ok=True)
    
    return download_path, download_urls_path

def search_images(driver, search_word):
    # google url 설정
    url = 'https://www.google.com/'

    # driver 설정
    driver.get(url)
    print("Google 홈페이지로 이동")

    # 검색어 입력 및 제출
    search_bar = driver.find_element(By.NAME, 'q')
    search_bar.send_keys(search_word)
    search_bar.submit()
    print(f"검색창에 '{search_word}' 입력 및 제출 완료")
    time.sleep(1)

    # '이미지' 탭으로 이동(현지 언어 지원)
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
            return None
    print("'이미지' 탭으로 이동 완료")

    return driver

def scroll_down(driver):
    # 스크롤 다운을 통한 이미지 로딩
    scroll_pause_time = 3  # 스크롤 사이의 대기 시간
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("스크롤 완료")

def get_thumbnails(driver):
    # 썸네일 이미지 URL 수집
    thumbnails_list = driver.find_elements(By.CSS_SELECTOR, '.YQ4gaf')
    num_thumbnails = len(thumbnails_list)
    if num_thumbnails == 0:
        print("수집된 이미지 url이 없습니다. 프로그램을 종료합니다")
        driver.quit()
        return None
    else: 
        print(f"이미지 url {num_thumbnails}개 수집 완료")
        return thumbnails_list

def download_images(driver, thumbnails_list, download_path, search_word, max_images):
    # 이미지 다운로드
    image_count_num = 0
    successful_downloads = 0 # 다운로드된 이미지 개수 추적
    downloaded_urls = set() # 중복 제거를 위해 다운로드된 이미지 URL을 저장하는 집합
    downloaded_images = []  # CSV 파일 형성을 위해 다운로드된 이미지와 URL을 저장하는 리스트

    for img in thumbnails_list:
        if successful_downloads >= max_images:
            break
        image_count_num += 1
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(img)).click()
            time.sleep(2) # 원본 이미지가 로드될 때까지 충분히 기다림
            big_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.sFlh5c.pT0Scc.iPVvYb'))
            )
            img_url = big_img.get_attribute("src") # 원본 이미지 주소 받기
            if img_url and img_url.startswith('http') and img_url not in downloaded_urls:
                print(f"다운로드 시도 중인 이미지 URL: {img_url}")
                time.sleep(1)
                img_name = f"{search_word}_{successful_downloads + 1}.jpg"
                img_path = os.path.join(download_path, img_name)
                urllib.request.urlretrieve(img_url, img_path)
                print(f"이미지 저장 완료: {search_word}_{successful_downloads + 1}.jpg")
                # 파일이 실제로 생성되었는지 확인
                if os.path.exists(img_path):
                    print(f"이미지 저장 완료: {img_path}")
                    successful_downloads += 1 # 성공한 다운로드 개수 증가
                    downloaded_urls.add(img_url)  # URL을 집합에 추가
                    downloaded_images.append((img_name, img_url))  # 이미지 이름과 URL을 리스트에 추가
                else:
                    print(f"이미지 저장 실패: {img_path}")
        except Exception as e:
            print(f"{image_count_num}번째 이미지 다운로드 오류 발생: {e}")

    return downloaded_images, successful_downloads

def save_urls_to_csv(downloaded_images, download_urls_path, search_word):
    # 다운로드된 URL을 CSV 파일로 저장
    df_img = pd.DataFrame(downloaded_images, columns=['이미지 이름', '이미지 URL'])
    urls_csv_file_path = os.path.join(download_urls_path, f"{search_word}_downloaded_urls.csv")
    df_img.to_csv(urls_csv_file_path, index=False, encoding='utf-8-sig')
    return urls_csv_file_path

def main():
    search_word = input("검색어를 입력하세요: ")
    max_images = 30 # 최대 다운로드할 이미지 수

    driver = setup_driver()
    download_path, download_urls_path = create_dir(search_word)
    driver = search_images(driver, search_word)
    
    if driver is None:
        return

    scroll_down(driver)
    thumbnails_list = get_thumbnails(driver)
    
    if thumbnails_list is None:
        return

    downloaded_images, successful_downloads = download_images(driver, thumbnails_list, download_path, search_word, max_images)
    urls_csv_file_path = save_urls_to_csv(downloaded_images, download_urls_path, search_word)

    print(f"성공한 다운로드 수: {successful_downloads}개")
    print(f"다운로드된 이미지 URL이 CSV 파일에 저장되었습니다: {urls_csv_file_path}")

    driver.quit()
    print("다운로드 완료")

if __name__ == "__main__":
    main()

# 참고자료
# https://velog.io/@ishikawakanata/Selenium%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%B4-%EA%B5%AC%EA%B8%80-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%9B%90%EB%B3%B8%EC%9C%BC%EB%A1%9C-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%98%EA%B8%B0
# https://velog.io/@now2466/%EC%9B%90%EB%B3%B8-%EC%9D%B4%EB%AF%B8%EC%A7%80-%ED%81%AC%EB%A1%A4%EB%A7%81-%ED%95%98%EB%8A%94%EB%B2%95
# https://wikidocs.net/177133
# https://velog.io/@holi/Pandas-Write-Files
# https://codingstep.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%EC%85%80%EB%A0%88%EB%8B%88%EC%9B%80-%ED%81%AC%EB%A1%AC-%EC%98%B5%EC%85%98-python-selenium-chrome-optionsFeat-headless-window-size-user-agent-etc