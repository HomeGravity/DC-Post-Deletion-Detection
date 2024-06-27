import requests
from bs4 import BeautifulSoup
from AddHeaders import *
from pprint import pprint
import time
import numpy as np
from basic import *

def InitResponse(url, data, CommentSortType):
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    form = soup.find("form", attrs={"id" : "_view_form_"})
    hidden = form.find_all("input", attrs={"type" : "hidden"})

    CommentData(data, hidden, CommentSortType)
    CommentHeadersUpdate(url)
    CommentResponse(data)


# data 값 초기값 설정
def CommentData(data, hidden, CommentSortType):
    data["id"] = hidden[10]["value"] # 갤러리 ID (게시글 접근 데이터)
    data["no"] = hidden[11]["value"] # 갤러리 게시글 ID (게시글 접근 데이터)
    data["cmt_id"] = hidden[10]["value"] # 갤러리 ID (댓글 접근 데이터)
    data["cmt_no"] = hidden[11]["value"] # 갤러리 게시글 ID (댓글 접근 데이터)
    data["focus_cno"] = None
    data["focus_pno"] = None
    data["e_s_n_o"] = hidden[14]["value"]
    data["comment_page"] = 1 # 댓글 Page
    data["sort"] = CommentSortType # 댓글 정렬 ex(등록순, 최신순, 답글순)
    data["prevCnt"] = 0
    data["board_type"] = None
    data["_GALLTYPE_"] = "M" # 갤러리 타입, 마이너갤, 미니갤 등..


# 댓글 헤더스 값 업데이트 함수 / 차단 방지
def CommentHeadersUpdate(Referer):
    CommentHeaders["Referer"] = Referer


# 댓글 요청 보내기
def CommentResponse(data):
    while True:
        response = requests.post("https://gall.dcinside.com/board/comment/", headers=CommentHeaders, data=data)
        response.raise_for_status()
        response = response.json()

        if response["comments"] is not None:

            # 나중에 데이터를 json으로 저장한 방법으로도 가능.
            CommentParse(response)
            data["comment_page"] += 1 # 댓글 Page
        
        else:
            print("마지막 페이지로 판단됨.")
            break
        
        # 5 ~ 10 이하 또는 미만의 실수 생성
        time.sleep(np.random.uniform(5, 10))


def CommentParse(response):
    # 줄바꿈
    print()
    for CommentsIndex in response["comments"]:
        for x1, y1 in CommentsIndex.items():
            # 불필요한 키-값 출력 제거
            if x1 != "gallog_icon" and int(CommentsIndex["no"]) != 0:
                CommentParseOutputDefinition(CommentsIndex, x1, y1)

        # 줄바꿈
        print()


# 출력 정의
def CommentParseOutputDefinition(CommentsIndex, x1, y1):
    if x1 == "memo" or x1 == "name" or x1 == "ip" or \
        x1 == "reg_date" or x1 == "user_id":
            
            if int(CommentsIndex["depth"]) == 0:
                print(OutputkeyManager(x1), ":", OutputValueManager(x1, y1))
            
            else:
                print("\t", OutputkeyManager(x1), ":", OutputValueManager(x1, y1))  

# 출력키 매니저
def OutputkeyManager(key):
    keyset = {
        "user_id" : "사용자 ID",
        "name" : "사용자 이름",
        "ip" : "사용자 IP",
        "reg_date" : "댓글 작성일",
        "memo" : "댓글 내용"
    }

    key = key
    for x1, y1 in keyset.items():
        key = key.replace(x1, y1)
    
    return key

# 출력값 매니저
def OutputValueManager(key, value):
    if value is not None and value != "":
        if "href" not in value and "written_dccon" not in value and "voice_wrap" not in value and \
            key != "reg_date":
                return value
        
        # 작성일 형식 변경
        elif key == "reg_date":
            return ChangCreationDate(value)

        # 댓글 내용에 링크가 포함된 경우 처리
        elif "href" in value:
            return OutputValueLinkParse(value)
        
        # 댓글 내용이 디시콘인 경우 처리
        elif "written_dccon" in value:
            return "내용이 '디시콘'으로 추정됨으로 출력을 제한함."
        
        # 댓글 내용이 보이스리플 경우 처리
        elif "written_dccon" in value:
            return "내용이 '보이스리플'으로 추정됨으로 출력을 제한함."

    else:
        return None


# 출력값에 만약 링크가 포함되어 있다면
def OutputValueLinkParse(value):
    soup = BeautifulSoup(value, "lxml")
    return soup.text


# 내가 지원할 것
# 갤러리 타입 자동설정
# 스크래핑 데이터를 로컬에 저장으로 재활용
# 코드 최적화


# D = 등록순, N = 최신순, R = 답글순
InitResponse(
    "https://gall.dcinside.com/mgallery/board/view/?id=vanced&no=4714",
    data,
    "D")

