# AGIDE(아지드)
## Auto Google Image Download Easily

![스크린샷 2024-06-28 170337](https://github.com/Andamiro-CrowlingProject/CrawlingProject/assets/165745047/45f77568-bc19-43b6-afe8-59c1f41dbce8)

사용자의 검색어를 바탕으로 구글에서 이미지를 크롤링하고, 로컬에 저장하며, 중복된 이미지를 찾을 수 있도록 합니다. 코드는 Python, PyQt5를 사용한 GUI, Selenium을 통한 웹 크롤링, OpenCV를 이용한 이미지 처리로 구성되어 있습니다.

### 기능
- 이미지 크롤링: 사용자의 검색어를 바탕으로 구글에서 이미지를 크롤링합니다.
- 이미지 저장: 크롤링한 이미지를 지정된 로컬 디렉토리에 저장합니다.
- 중복 이미지 탐지: 유사도 임계값을 기준으로 중복된 이미지를 탐지하고 보고합니다.
- GUI 인터페이스: 검색어 입력, 다운로드할 이미지 수 설정, 저장 디렉토리 지정, 작업 프로세스 등 사용자에게 친화적인 인터페이스를 제공합니다.

### 사전 준비
#### 실행하기 전 다음을 설치했는지 확인하시길 바랍니다.
- Python 3.6+
- pip(Python 패키지 관리자)

#### 필요한 라이브러리를 설치합니다.
```
pip install -r requirements.txt
```
#### 라이브러리
![PyQt5](https://img.shields.io/badge/PyQt5-00FF00)
![Selenium](https://img.shields.io/badge/Selenium-2E9AFE)
![requests](https://img.shields.io/badge/requests-848484)
![OpenCV](https://img.shields.io/badge/OpenCV-FF0000)
![pandas](https://img.shields.io/badge/pandas-380B61)
![numpy](https://img.shields.io/badge/numpy-01A9DB)
![Pillow(PIL)](https://img.shields.io/badge/Pillow-81BEF7)

### 사용법

- 프로그램 파일을 실행합니다.
```
python CrawlingGUI.py
```
![KakaoTalk_20240628_173003971](https://github.com/Andamiro-CrowlingProject/CrawlingProject/assets/165745047/119c9f44-5f0e-49da-bf84-c676c3e6ac0e)

- 검색어: 크롤링할 이미지의 검색어를 입력합니다.
- 이미지 개수: 다운로드할 이미지의 개수를 입력합니다.
- 저장 경로: 다운로드한 이미지를 저장할 경로를 입력합니다.
- 검색 버튼: "검색" 버튼을 클릭하여 크롤링을 시작합니다.
- 작업 프로세스 창을 통해 중복 이미지 검출 및 이미지 출처를 확인할 수 있습니다.  

### 주의사항
- 네트워크가 원활한 장소에서 실행하세요.
- Chrome 브라우저를 사용하여 크롤링을 수행합니다. Google Chrome이 설치되어 있는지 확인하세요.
- 'chromedriver-autoinstaller' 패키지는 적절한 버전의 ChromeDriver를 자동으로 다운로드합니다.
- 과도한 요청은 IP 차단 등의 문제가 발생할 수 있습니다.

### 활용방안

#### 스케줄링을 통한 자동 이미지 다운로드

로컬에서 스케줄링을 통해 자동으로 단위 시간마다 이미지를 다운로드할 수 있습니다.

### 라이센스
이 프로젝트는 MIT 라이센스에 따라 라이센스가 부여됩니다. 자세한 내용은 LICENSE 파일을 참고하세요.
