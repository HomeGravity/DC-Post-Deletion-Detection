from AddHeaders import *
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
from basic import *

# requests 로 구현하다 안되서 selenium 으로 구현
def SeleniumSettings(HeadlessMod):
    # 셀레니움 설정
    chrome_options = Options()
    chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--lang=ko")
    chrome_options.add_argument("--window-size=1920, 1080")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--log-level=3')
    
    # 헤드리스 모드 활성화 및 비활성화 설정
    if HeadlessMod:
        chrome_options.add_argument("headless")

    # 헤더스 적용
    for k, v in headers.items():
        chrome_options.add_argument(f"{k}={v}")
        
    # dns 적용으로 디시 광고 차단
    local_state = {
        "dns_over_https.mode": "secure",
        "dns_over_https.templates": "https://dns.adguard.com/dns-query",
    }
    chrome_options.add_experimental_option('localState', local_state)

    service = Service(excutable_path=ChromeDriverManager().install()) 
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('chrome://settings/security')
    driver.implicitly_wait(10)
    time.sleep(2)
    
    return driver

def DCLogin(driver, id, password):
    driver.get("https://www.dcinside.com/")
    driver.implicitly_wait(20)

    id_ = driver.find_element(By.NAME, "user_id")
    id_.click()
    id_.send_keys(id)
    time.sleep(2)

    pass_ = driver.find_element(By.NAME, "pw")
    pass_.click()
    pass_.send_keys(password)
    time.sleep(2)

    dc_login_btn = driver.find_element(By.ID, 'login_ok')
    dc_login_btn.click()
    time.sleep(2)
    
    return driver
    
def SeleniumLoactionURL(driver, title, desc, url):
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        time.sleep(2)
        
        # 타이틀글 입력
        driver = titleInput(driver, title)
        
        # 설명글 입력
        driver = descInput(driver, desc)

        # 버튼 클릭
        driver.find_element(By.CSS_SELECTOR, "#modify > div.btn_box.write.fr > button.btn_blue.write").click()

    except Exception as e:
        # 문제 생기면 바로 종료.
        print("예상치 못한 오류 발생\n", e)
        sys.exit(1)


# 타이틀글 입력 함수
def titleInput(driver, title):
    # 타이틀글 입력
    title_element = "subject"
    driver.find_element(By.ID, title_element).clear()
    time.sleep(1)
    # 원하는 타이틀 입력
    driver.find_element(By.ID, title_element).send_keys(title)
    
    return driver


# 설명글 입력 함수
def descInput(driver, desc):
    # iframe 찾기 / iframe 를 tag명으로 찾으니 헤드리스 모드에서 오류남.
    iframe = driver.find_element(By.NAME, 'tx_canvas_wysiwyg')
    # iframe으로 전환
    driver.switch_to.frame(iframe)
    time.sleep(3)
    
    # 설명글 입력
    desc_element = "tx-content-container"
    driver.find_element(By.CLASS_NAME, desc_element).clear()
    time.sleep(1)
    # 원하는 설명글 입력
    driver.find_element(By.CLASS_NAME, desc_element).send_keys(desc)
    # 기본 페이지로 전환
    driver.switch_to.default_content()
    time.sleep(3)
    
    return driver

# 셀레니움 실행함수
def driverStart(IsDriverRun, HeadlessMod):
    if IsDriverRun:
        # 1. 셀레니움 초기화

        # 1.1 디시인사이드 로그인 계정
        DCLoginAccount = OpenJson("login.json")

        # 1.2 디시 게시글 작성 함수
        driver = SeleniumSettings(HeadlessMod)
        driver = DCLogin(driver, DCLoginAccount["login id"], DCLoginAccount["login password"])

    # False 이면 driver 초기화를 필수로 해야하기 때문에 아무 의미도 없는 None로 설정해서 driver를 초기화함.
    else:
        driver = None

    return driver, IsDriverRun

if __name__ == '__main__':
    driver, IsDriverRun = driverStart(False, False) # 드라이버 실행 여부, 헤드리스 모드 실행 실행

    if IsDriverRun:
        SeleniumLoactionURL(driver, "title", "desc", "url")

    
    
