import json
import datetime
import re
import time

def OpenJson(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def SaveJSON(filename, data):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def CurrentTime():
    dt = datetime.datetime.now()
    
    if dt.hour < 12:
        meridiem = "오전"

    else:
        meridiem = "오후"
    
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    
    return dt.strftime(f"%Y/%m/%d {meridiem} {hour}:%M:%S")


# 작성일 형식 변경
def ChangCreationDate(date_text):
    try:
        # 연도가 포함된 경우와 포함되지 않은 경우 구분
        if len(date_text.split(".")) == 3:
            # 연도, 월일, 시분초가 포함된 경우
            dt = datetime.datetime.strptime(date_text, "%Y.%m.%d %H:%M:%S")
        else:
            # 월일, 시분초만 포함된 경우
            dt = datetime.datetime.strptime(date_text, "%m.%d %H:%M:%S")
            # 현재 년도 입력
            dt = dt.replace(year=datetime.datetime.now().year)
        
        # 오전/오후 구분
        if dt.hour < 12:
            meridiem = "오전"
        else:
            meridiem = "오후"
        
        # 12시간제로 변환
        hour = dt.hour % 12
        if hour == 0:
            hour = 12
        
        # 지정된 형식으로 변환
        return dt.strftime(f"%Y/%m/%d {meridiem} {hour}:%M:%S")
    
    except ValueError as e:
        return f"날짜 형식이 올바르지 않습니다. {e}"


# 쿼리 제거
def gall_id(url):
    # '?' 를 기준으로 URL을 분리하여 쿼리 파라미터 부분을 얻는다
    query_str = url.split('?')[-1]

    # '&'를 기준으로 각 쿼리 파라미터를 분리한다
    query_params = query_str.split('&')

    # 각 쿼리 파라미터를 순회하며 'id' 파라미터의 값을 찾는다
    id_value = None
    for param in query_params:
        if param.startswith('id='):
            id_value = param.split('=')[-1]
            break

    return id_value



# 불필요한 텍스트 삭제
def OnlyTEXT(text):
    return re.sub(r'[^a-zA-Z0-9가-힣]', '', text)

# IP 괄호는 지우고 마침표는 유지
def RemoveBrackets(text):
    if text is not None:
        return re.sub(r'\(|\)', '', text)

    return None

def URLCheck(URL):
    OriginalURL = URL.split('/')
    return f"https://gall.dcinside.com/mgallery/board/view?id={OriginalURL[3]}&no={OriginalURL[4]}"