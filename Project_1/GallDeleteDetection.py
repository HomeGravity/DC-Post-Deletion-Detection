import requests
from bs4 import BeautifulSoup
from AddHeaders import *
import time
import numpy as np
from pprint import pprint
import os
from GallPostWrite import *
from basic import *


def InitResponse(
    URL,
    WebURL,
    driver,
    GallDataDict,
    FileTopic,
    definedStartPage, 
    definedLastPage,
    definedBreak
    ):
    
    # 전역변수 breakpoint
    global breakPoint
    
    breakPoint = True
    index = definedStartPage
    
    if definedStartPage <= 0 or definedLastPage <= 0:
        print(f"[{FileTopic} 토픽] 시작 & 끝 입력 페이지는 0보다 높아야합니다.")
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
            print(f"[{FileTopic} 토픽] {index} 페이지 완료!")
            
            Getpropertydata(response.text, GallDataDict, FileTopic, WebURL, driver)
            index += 1
            time.sleep(np.random.uniform(5, 10))

        else:
            print("break status: " + response.status_code)
            break


def Getpropertydata(source, GallDataDict, FileTopic, WebURL, driver):
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
        
        subject_inner_check = i.find("p", attrs={"class" : "subject_inner"})
        if subject_inner_check:
            PostTopic = None if (temp := subject_inner_check) is None else temp.get_text().strip()
        
        else:
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
        
        
        
        # 토픽이 설문 또는 공지이면 수집 제외, 토픽 속성 수정 필요
        if PostTopic != "설문" and PostTopic != "공지":
            GallDataDict[int(Postcreationnumber)] = {
                f"게시글 번호": int(Postcreationnumber),
                f"게시글 토픽": OnlyTEXT(PostTopic),
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
                f"게시글 탐지 권한": "Allow detection",
                f"게시글 수집시간": CurrentTime(),
                f"게시글 삭제 탐지시간": None,
                f"비고": None
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
        FilePath = FileTopic + " " +"게시글.json"
        
        # 스크래핑 작업이 종료되면 dataprocessing 작업이 실행됨.
        GallDataProcessing(GallDataDict, FilePath)

        # 데이터 비교
        GallDataComparison(GallDataDict, FilePath, FileTopic, LastPostOutputConditions, WebURL, driver)
        
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
                    
                    # 게시글 탐지 권한, 비고, 게시글 수집시간, 게시글 삭제 탐지시간은 업데이트 하지 않음.
                    if x2 != "게시글 탐지 권한" or x2 != "비고" or \
                        x2 != "게시글 수집시간" or x2 != "게시글 삭제 탐지시간":
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



# 게시글이 삭제됐는지 확인하는 함수
def CheckPostDeletion(URL):
    response = requests.get(URL, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        Update_Topic = soup.find("span", attrs={"class": "title_headtext"})
        
        # 불필요한 문자 제거
        CheckResult = OnlyTEXT(Update_Topic.text)
        
    else:
        CheckResult = f"게시글이 삭제됐거나 찾을 수 없음 - Code: {response.status_code}"
        
    return CheckResult

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
    
    # 리디렉션을 방지하기 위해 쿼리를 추가함.
    CheckPost = CheckPostDeletion(URLCheck(y1["게시글 링크"]))
    
    # detection_settings 에 해당 키값이 있을때만
    if str(x1) in detection_settings[FileTopic]:
        
        # detection_settings 에 권한 설정 값이 False 또는 CheckPost 가 실행되면
        if detection_settings[FileTopic][str(x1)] == False or \
            CheckPost is not None:
            
                # 게시글 토픽이 변경된건 삭제된게 아니니 삭제판정을 하지않지만, 
                # 진짜로 삭제판정된건 계속 탐지를 하겠다.
                if "Code" in CheckPost:
                    CheckPostText = CheckPost
                    
                    # 삭제됨, 계속 탐지를 허용
                    DetectionText = "Allow detection"
                
                else:
                    CheckPostText = f"게시글 토픽이 '{CheckPost}'으로 변경됨"
                    
                    # 삭제된 건 아님, 계속 탐지를 허용 안 함
                    DetectionText = "Not Allow detection"
                    
                
                y1["비고"] = CheckPostText
                existing_data[x1]["비고"] = CheckPostText
                
                y1["게시글 탐지 권한"] = DetectionText
                existing_data[x1]["게시글 탐지 권한"] = DetectionText



        # 탐지 권한 값이 True이면 탐지를 허용함으로 판정.
        elif detection_settings[FileTopic][str(x1)] == True and \
            y1["게시글 탐지 권한"] != "Allow detection":
                
                y1["게시글 탐지 권한"] = "Allow detection"
                existing_data[x1]["게시글 탐지 권한"] = "Allow detection"
        
    
    # x1이 detection_settings 파일에 키값 없는 경우 초기값을 허용함으로 설정.
    else:
        if FileTopic not in detection_settings:
            detection_settings[FileTopic] = {}
        
        if str(x1) not in detection_settings[FileTopic]:
            detection_settings[FileTopic][str(x1)] = True
    
    
    # 시간 업데이트
    if existing_data[x1]["게시글 삭제 탐지시간"] is None:
        y1["게시글 삭제 탐지시간"] = CurrentTime()
        existing_data[x1]["게시글 삭제 탐지시간"] = CurrentTime()
            
    
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
    
    print()
    return TEXTMerge

# 데이터 비교
def GallDataComparison(GallDataDict, FilePath, FileTopic, LastPostOutputConditions, WebURL, driver):
    
    if os.path.isfile(FilePath):

        TEXTMerge = ""
        
        existing_data = OpenJson(FilePath)
        detection_settings = DetectionSettings()
        
        print(f"\n[{FileTopic} 토픽] 삭제된 게시글로 추정되는 게시글을 출력▼")
        count = 0
        for x1, y1 in existing_data.items():
            
            # 삭제된 글 출력
            # 게시글 탐지 권한 타입 Allow detection 인것만 출력
            # 기존 100 번째 배열이 다른 페이지로 넘어가면 삭제 됐다고 뜨는 것을 방지, 페이지 제한모드에서는 100으로 설정하고 전체 페이지 모드에서는 0으로 설정
            if int(x1) not in GallDataDict and \
                y1["게시글 탐지 권한"] == "Allow detection" and \
                    y1["게시글 배열번호"] != LastPostOutputConditions and \
                        min(GallDataDict) <= int(x1):
                            
                            print(f"\n{x1}번 게시글")
                            TEXTMerge += f"\n{x1}번 게시글\n"
                            
                            # 탐지 권한 체크
                            existing_data, y1, detection_settings = DectionSettingsCheck(existing_data, x1, y1, FileTopic, detection_settings)
                            
                            TEXTMerge += AddTEXT(y1) # 탐지 내역 추가
                            TEXTMerge += "\n" # 줄바꿈
                            
                            count += 1
                            
                            time.sleep(np.random.uniform(3, 6))


        if count == 0:
            print(f"[{FileTopic} 토픽] 삭제된 게시글이 없음으로 추정.\n")
            TEXTMerge += "\n삭제된 게시글이 없음으로 추정.\n"
        
        # count 가 0 이 아니면서 이전 내역이랑 동일하지 않을때만
        if count != 0:
            # 디시 자동 글쓰기 함수
            SeleniumLoactionURL(driver, f"[{CurrentTime()}] {FileTopic} - 글삭제 감지 알림", f"{TEXTMerge}", WebURL)

            # 변경사항을 저장
            SaveJSON(FilePath, existing_data)
            
            SaveJSON("탐지 권한 설정.json", DetectionSettingsDescendingSort(detection_settings))



RestartDelay = 60 * 15 # 15분 간격으로 수정
print(f"\n{RestartDelay:,.0f}초 (약 {RestartDelay // 60:,.0f}분) 마다 실행됨\n만약 프로그램을 종료하고 싶다면 'Ctrl+C'를 누르세요.\n")
time.sleep(3)
print("탐지 시작!")


# 디시인사이드 로그인 계정
DCLoginAccount = OpenJson("login.json")

# 디시 게시글 작성 함수
driver = SeleniumSettings(False)
driver = DCLogin(driver, DCLoginAccount["login id"], DCLoginAccount["login password"])


# 마이너 갤러리만 지원함.
# URL1 = 탐지할 게시글 토픽
# URL2 = 탐지한 결과를 업데이트할 곳


while True:
    try:
        InitResponse(
            "https://gall.dcinside.com/mgallery/board/lists/?id=vanced&page=%s&list_num=100&search_head=60", 
            "https://gall.dcinside.com/mgallery/board/modify/?id=vanced&no=4714",
            driver,
        {}, "질문",
        1, 1, False
        ) # definedBreak 이가 False 이면 definedLastPage 조건이 무효화됨.


        InitResponse(
            "https://gall.dcinside.com/mgallery/board/lists/?id=vanced&page=%s&list_num=100&search_head=130", 
            "https://gall.dcinside.com/mgallery/board/modify/?id=vanced&no=4703",
            driver,
        {}, "핑프",
        1, 1, False
        ) # definedBreak 이가 False 이면 definedLastPage 조건이 무효화됨.
        
        time.sleep(RestartDelay)
        
        
    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        break