import requests
from bs4 import BeautifulSoup
from AddHeaders import *
import time
import numpy as np
import json
import datetime
from pprint import pprint
import os
from GallPostWrite import *


def OpenJson(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def SaveJSON(filename, data):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# 디시인사이드 로그인 계정
DCLoginAccount = OpenJson("login.json")

driver = SeleniumSettings()
driver = DCLogin(driver, DCLoginAccount["login id"], DCLoginAccount["login password"])

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


def InitResponse(
    URL,
    WebURL,
    GallDataDict,
    DataSaveTopic,
    definedStartPage, 
    definedLastPage, 
    definedBreak
    ):
    
    # 전역변수 breakpoint
    global breakPoint
    
    breakPoint = True
    index = definedStartPage
    
    if definedStartPage <= 0 or definedLastPage <= 0:
        print(f"[{DataSaveTopic} 토픽] 시작 & 끝 입력 페이지는 0보다 높아야합니다.")
        return
    
    if definedBreak:
        print("\n페이지 제한 모드 실행 중...\n")
    
    else:
        print("\n전체 페이지 모드 실행 중...\n")
    
    while breakPoint:
        response = requests.get(URL % index, headers=headers, timeout=10)
        response.raise_for_status()
        
        if index == definedLastPage and definedBreak:
            breakPoint = False
        
        if response.status_code == 200:
            print(f"[{DataSaveTopic} 토픽] {index} 페이지 완료!")
            
            Getpropertydata(response.text, GallDataDict, DataSaveTopic, WebURL)
            index += 1
            time.sleep(np.random.uniform(5, 10))

        else:
            print("break status: " + response.status_code)
            break

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

def Getpropertydata(source, GallDataDict, DataSaveTopic, WebURL):
    global breakPoint
    
    soup = BeautifulSoup(source, "lxml")
    properties = soup.find_all("tr", attrs="ub-content")

    # 페이지 제한 모드 출력 게시글 오탐지 설정값
    LastPostOutputConditions = 100
    
    # 게시글 배열 번호
    PostArr = 1
        
    for i in properties:
        # 게시글 번호
        Postcreationnumber = None if (temp := i.find("td", attrs={"class" : "gall_num"})) is None else temp.get_text().strip()
        # 게시글 토픽
        PostTopic = None if (temp := i.find("td", attrs={"class" : "gall_subject"})) is None else temp.get_text().strip()
        # 게시글 이름
        PostTitle = None if (temp := i.find("a")) is None else temp.get_text().strip()
        # 게시글 링크
        PostLink = None if (temp := i.find("a")) is None else "https://gall.dcinside.com/" + str(gall_id(temp["href"])) + "/" + str(Postcreationnumber)
        # 게시글 댓글 수
        PostCommentNumber = 0 if (temp := i.find("span", attrs={"class": "reply_num"})) is None else int(temp.get_text().strip().replace("[", "").replace("]", ""))
        # 사용자 이름
        PostUser = None if (temp := i.find("span", attrs={"class": "nickname"})) is None else temp.get_text().strip()
        # 사용자 식별코드
        temp_id = i.find("td", attrs={"class": "gall_writer ub-writer"})
        PostUserCode = temp_id.get("data-uid") if temp_id and temp_id.get("data-uid") and len(temp_id.get("data-uid").strip()) != 0 else None
        # 사용자 IP
        PostUserIp = None if (temp := i.find("span", attrs={"class": "ip"})) is None else temp.get_text().strip()
        # 게시글 작성일
        PostDate = None if (temp := i.find("td", attrs={"class": "gall_date"})) is None else temp.get_text().strip()
        # 게시글 조회수
        PostViewCount = None if (temp := i.find("td", attrs={"class": "gall_count"})) is None else temp.get_text().strip()
        # 게시글 추천 수
        PostLiveNumber = None if (temp := i.find("td", attrs={"class": "gall_recommend"})) is None else temp.get_text().strip()
        
        # 토픽이 설문이면 수집 제외
        if PostTopic != "설문":
            GallDataDict[int(Postcreationnumber)] = {
                f"게시글 번호": int(Postcreationnumber),
                f"게시글 토픽": PostTopic,
                f"게시글 이름": PostTitle,
                f"게시글 링크": PostLink,
                f"게시글 댓글수": PostCommentNumber,
                f"사용자 이름": PostUser,
                f"사용자 식별코드": PostUserCode,
                f"사용자 IP": PostUserIp,
                f"게시글 작성일": PostDate,
                f"게시글 조회수": int(PostViewCount),
                f"게시글 추천수": int(PostLiveNumber),
                f"게시글 배열번호": PostArr,
                f"게시글 탐지 권한": "Allow detection"
            }
            

            # 게시글 배열 번호
            PostArr += 1

    # 게시글 마지막 배열 값이 101보다 작으면
    # Post 배열이 101보다 낮으면서 동시에 breakpoint가 True 상태이면 실행.
    if PostArr < 101 and breakPoint == True:
        print("마지막 페이지로 판단됨으로 break 작동")
        breakPoint = False
        
        # 전체 페이지를 수집모드에서는 오탐지가 발생하지 않아서 0으로 설정
        LastPostOutputConditions = 0
    
    if breakPoint == False:
        # 파일명
        FilePath = DataSaveTopic + " " +"게시글.json"
        
        # 스크래핑 작업이 종료되면 dataprocessing 작업이 실행됨.
        GallDataProcessing(GallDataDict, FilePath)

        # 데이터 비교
        GallDataComparison(GallDataDict, FilePath, DataSaveTopic, LastPostOutputConditions, WebURL)
        
        # 초기화
        GallDataDict = {}


# 이 함수는 스크래핑된 데이터를 기존 파일에 업데이트하고 추가하며 파일로 만듭니다.
def GallDataProcessing(GallDataDict, FilePath):
    # 파일이 존재하는 경우

    if os.path.isfile(FilePath):
        existing_data = OpenJson(FilePath)
        AddNewPost = True
        
        for x1, y1 in GallDataDict.items():
            # key 비교, 기존 데이터와 신규 데이터와 비교해서 같은 keys 변경작업을 실행함.
            if str(x1) in existing_data.keys():
                for x2, y2 in y1.items():
                    if x2 != "게시글 탐지 권한": # 게시글 탐지 권한은 업데이트 하지 않음.
                        existing_data[str(x1)][x2] = y2

            else:
                existing_data[x1] = y1
                
                # 추가된 게시글 출력
                if AddNewPost == True:
                    print("\n새로 추가된 게시글\n")
                    AddNewPost = False
                
                for x2, y2 in y1.items():
                    print("\t", x2, ":", y2)
                print()
            
                
        # Key를 기준으로 내림차순 정렬 및 저장
        dataSave = dict(sorted(existing_data.items(), key=lambda item: int(item[0]), reverse=True))

    else:
        dataSave = GallDataDict
    

    SaveJSON(FilePath, dataSave)

# 탐지 권한 설정을 불러오는 함수
def DetectionSettings():
    # 파일 처리
    try:
        detection_settings = OpenJson("탐지 권한 설정.json")
    
    # 파일에 아무것도 없을 경우
    except json.decoder.JSONDecodeError:
        detection_settings = {}

    return detection_settings


# 게시글 탐지 권한을 수정하는 함수
def DectionSettingsCheck(existing_data, x1, y1, FileTopic, detection_settings):
    # 탐지 권한 값이 False이면 탐지를 허용안함으로 판정.
    if str(x1) in detection_settings[FileTopic]:
        if detection_settings[FileTopic][str(x1)] == False:
            
            y1["게시글 탐지 권한"] = "Not Allow detection"
            existing_data[x1]["게시글 탐지 권한"] = "Not Allow detection"
        
        # 탐지 권한 값이 True이면 탐지를 허용함으로 판정.
        elif detection_settings[FileTopic][str(x1)] == True and \
            y1["게시글 탐지 권한"] != "Allow detection":
                
                y1["게시글 탐지 권한"] = "Allow detection"
                existing_data[x1]["게시글 탐지 권한"] = "Allow detection"
    

    # x1이 detection_settings 파일에 없는 경우 예외로 허용함으로 설정.
    else:
        if FileTopic not in detection_settings:
            detection_settings[FileTopic] = {}
        
        if str(x1) not in detection_settings[FileTopic]:
            detection_settings[FileTopic][str(x1)] = True
    
    return existing_data, y1, detection_settings


# 게시글 탐지 권한 데잍터 내림차순 정렬
def DetectionSettingsDescendingSort(data):
    sorted_data = {
    k: dict(sorted(v.items(), key=lambda x: int(x[0]), reverse=True))
    for k, v in data.items()
    }
    
    return sorted_data

# TEXTMerge 변수에 텍스트 추가 및 출력
def AddTEXT(y1):
    TEXTMerge = ""
    for x2, y2 in y1.items():
        print(f"\t {x2} : {y2}")
        TEXTMerge += f"{x2} : {y2}\n"
    
    return TEXTMerge

# 데이터 비교
def GallDataComparison(GallDataDict, FilePath, FileTopic, LastPostOutputConditions, WebURL):
    
    if os.path.isfile(FilePath):

        TEXTMerge = ""
        
        existing_data = OpenJson(FilePath)
        detection_settings = DetectionSettings()
        
        print(f"\n[{FileTopic} 토픽] 삭제된 게시글로 추정되는 게시글을 출력▼")

        count = 0
        for x1, y1 in existing_data.items():
            
            # 삭제된 글 출력
            # 게시글 탐지 권한 타입 Allow detection 인것만 출력
            if int(x1) not in GallDataDict.keys() and \
                y1["게시글 탐지 권한"] == "Allow detection" and \
                    y1["게시글 배열번호"] != LastPostOutputConditions: # 기존 100 번째 배열이 다른 페이지로 넘어가면 삭제 됐다고 뜨는 것을 방지, 페이지 제한모드에서는 100으로 설정하고 전체 페이지 모드에서는 0으로 설정
                    
                        print(f"\n{x1}번 게시글")
                        TEXTMerge += f"\n{x1}번 게시글\n"
                        
                        # 탐지 권한 체크
                        existing_data, y1, detection_settings = DectionSettingsCheck(existing_data, x1, y1, FileTopic, detection_settings)
                        
                        TEXTMerge += AddTEXT(y1) # 탐지 내역 추가
                        TEXTMerge += "\n" # 줄바꿈
                        
                        count += 1


        if count == 0:
            print(f"[{FileTopic} 토픽] 삭제된 게시글이 없음으로 추정.\n")
        
        # count 가 0 이 아니면서 이전 내역이랑 동일하지 않을때만
        if count != 0:
            # 디시 자동 글쓰기 함수
            SeleniumLoactionURL(driver, f"[{CurrentTime()}] {FileTopic} - 글삭제 감지 알림", f"{TEXTMerge}", WebURL)

            # 변경사항을 저장
            SaveJSON(FilePath, existing_data)
            
            SaveJSON("탐지 권한 설정.json", DetectionSettingsDescendingSort(detection_settings))


RestartDelay = 60 * 5 # 5분 간격으로 수정
print(f"\n{RestartDelay:,.0f}초 (약 {RestartDelay // 60:,.0f}분) 마다 실행됨\n만약 프로그램을 종료하고 싶다면 'Ctrl+C'를 누르세요.\n")
time.sleep(3)
print("탐지 시작!")

while True:
    try:
        InitResponse(
            "https://gall.dcinside.com/mgallery/board/lists/?id=vanced&page=%s&list_num=100&search_head=60", 
            "https://gall.dcinside.com/mgallery/board/modify/?id=vanced&no=4714",
        {}, "질문",
        1, 1, False
        ) # definedBreak 이가 False 이면 definedLastPage 조건이 무효화됨.


        InitResponse(
            "https://gall.dcinside.com/mgallery/board/lists/?id=vanced&page=%s&list_num=100&search_head=130", 
            "https://gall.dcinside.com/mgallery/board/modify/?id=vanced&no=4703",
        {}, "핑프",
        1, 2, False
        ) # definedBreak 이가 False 이면 definedLastPage 조건이 무효화됨.
        
        time.sleep(RestartDelay)
        
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        break