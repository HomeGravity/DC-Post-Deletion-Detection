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


# requests 로 구현하다 안되서 selenium 으로 구현
def SeleniumSettings(HeadlessMod):
    # 셀레니움 설정
    chrome_options = Options()
    chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--lang=ko")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    
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
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(2)
    
    # 타이틀글 입력
    driver.find_element(By.ID, "subject").clear()
    time.sleep(1)
    # 원하는 타이틀 입력
    driver.find_element(By.ID, "subject").send_keys(title)
    
    # iframe 찾기 / iframe 를 tag명으로 찾으니 헤드리스 모드에서 오류남.
    iframe = driver.find_element(By.NAME, 'tx_canvas_wysiwyg')
    # iframe으로 전환
    driver.switch_to.frame(iframe)
    time.sleep(3)
    
    # 설명글 입력
    driver.find_element(By.CLASS_NAME, "tx-content-container").clear()
    time.sleep(1)
    # 원하는 설명글 입력
    driver.find_element(By.CLASS_NAME, "tx-content-container").send_keys(desc)
    # 기본 페이지로 전환
    driver.switch_to.default_content()
    time.sleep(3)

    # 버튼 클릭
    driver.find_element(By.CSS_SELECTOR, "#modify > div.btn_box.write.fr > button.btn_blue.write").click()


if __name__ == '__main__':
    driver = SeleniumSettings(True)
    driver = DCLogin(driver, "id", "password")
    SeleniumLoactionURL(driver, "질문글", "설명글")
    
    
