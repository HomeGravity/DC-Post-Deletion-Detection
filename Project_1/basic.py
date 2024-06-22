import json
import datetime

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