'''민방위 교육 일정 조회
출처: https://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/contents/civil_defense/SDIJKM1205.jsp?emgPage=Y&menuSeq=50
'''
import requests
from datetime import date, datetime


# 시도 목록
SIDO_LIST = [
    ("서울특별시", "6110000"),
    ("부산광역시", "6260000"),
    ("대구광역시", "6270000"),
    ("인천광역시", "6280000"),
    ("광주광역시", "6290000"),
    ("대전광역시", "6300000"),
    ("울산광역시", "6310000"),
    ("세종특별자치시", "5690000"),
    ("경기도", "6410000"),
    ("강원특별자치도", "6530000"),
    ("충청북도", "6430000"),
    ("충청남도", "6440000"),
    ("전북특별자치도", "6540000"),
    ("전라남도", "6460000"),
    ("경상북도", "6470000"),
    ("경상남도", "6480000"),
    ("제주특별자치도", "6500000"),
]

# 시군구 목록 (동적으로 채워짐.)
SIGUNGU_LIST = None

# 교육대상 코드 (2년차인경우 31(민방위대 편입 1~2년차대원), 33(민방위대 편입 2년차대원) 모두 조회)
EDU_TARGET_CODES = ["31"]

# 조회기간 (오늘 ~ 연말)
START_DATE = date.today()
END_DATE = date(START_DATE.year, 12, 31)

# 교육시간 (0: 평일, 1: 야간, 2: 주말)
EDU_TIME = "0"


def make_req_data(sido_code, sigungu_code, edu_target_code, page_index=1, page_size=0):
    return {
        "selectList": {
            "searchGb":"",
            "firstIndex":"1",
            "lastIndex":"1",
            "pageIndex":str(page_index),
            "pageSize":str(page_size),
            "pageUnit":"10",
            "recordCountPerPage":"10",
            "sbscrbSttus":"",
            "searchCondition":"",
            "search_val":"",
            "search_key":"",
            "searchCdKey":"",
            "parntsBdongCd":"",
            "emgncContactNtwkSeCd":"2",
            "orgSeCd":"02",
            "q_area_cd_3":"",
            "q_area_cd_2":sigungu_code,
            "q_area_cd_1":sido_code,
            "q_strdate":f"{START_DATE:%Y%m%d}",
            "q_enddate":f"{END_DATE:%Y%m%d}",
            "q_onefour":"",
            "hdaySe":EDU_TIME,
            "edcTgtSeCd":edu_target_code,
            "cvdpyCpsCode":"",
            "cvdEduSeCode":"",
            "edYmd":"",
            "edSno":"",
            "searchDate1":f"{START_DATE:%Y%m%d}",
            "searchDate2":f"{END_DATE:%Y%m%d}",
            "rdn_code":""
        }
    }


def convert_edu_list(edu_sch_list, ampm_filter=None):
    weekday_map = ["월", "화", "수", "목", "금", "토", "일"]
    result = []
    seen = set()  # 중복 방지용 (일정+장소 조합 저장)

    for item in edu_sch_list:
        # 교육 일정이 없는 경우 빈 dict 이므로 건너뜀.
        if not item:
            continue

        # 날짜/시간 변환
        date_obj = datetime.strptime(item["ED_YMD"], "%Y%m%d")
        weekday = weekday_map[date_obj.weekday()]

        if ampm_filter == "1" and item["edcBeginTime"] >= "1200":
            continue  # 오전만 필터링
        elif ampm_filter == "2" and item["edcBeginTime"] < "1200":
            continue  # 오후만 필터링

        schedule = (
            f"{date_obj:%Y-%m-%d}({weekday}) "
            f"{item['edcBeginTime'][:2]}:{item['edcBeginTime'][2:]}-"
            f"{item['edcEndTime'][:2]}:{item['edcEndTime'][2:]}"
        )
        place = item["EDU_PLC_BOTTOM"]

        key = (schedule, place)
        if key not in seen:  # 중복 제거
            seen.add(key)
            result.append({
                "schedule": schedule,
                "place": place
            })

    return result


def fetch_schedules(sido_code, sigungu_code, edu_target_code, ampm_filter=None):
    page = 1
    page_size = None

    schedules = []
    while page_size is None or page <= page_size:
        req_data = make_req_data(sido_code, sigungu_code, edu_target_code, page, page_size)
        response = requests.post("https://www.safekorea.go.kr/idsiSFK/sfk/cs/cvi/edtr/selectEduSchList2.do", json=req_data).json()
        schedules.extend(convert_edu_list(response["eduShcList"], ampm_filter))
        page_size = response["rtnResult"]["pageSize"]
        page += 1

    return schedules


if __name__ == "__main__":
    print("### 민방위(1~2년차) 평일(주간) 집합교육 일정 조회 ###", end="\n\n\n")

    # 시도 선택
    for i, (name, _) in enumerate(SIDO_LIST, start=1):
        print(f"{i:2d}. {name}")
    selected_index = input(f"\n## 시도를 선택해주세요 (예. {SIDO_LIST[0][0]} -> 1 입력): ")
    print("\n")
    selected_sido = SIDO_LIST[int(selected_index) - 1]

    # 시군구 목록 조회
    response = requests.get(f"https://www.safekorea.go.kr/idsiSFK/neo/ext/json/arcd/hd/{selected_sido[1]}/hd_sgg.json").json()
    SIGUNGU_LIST = [(item["ORG_NM"], item["ORG_CD"]) for item in response]

    # 민방위 연차 선택
    selected_year = input("## 민방위대 편입연차 선택 (1: 1년차, 2: 2년차): ")
    if selected_year == "2":
        EDU_TARGET_CODES.append("33")
    else:
        selected_year = "1"
    print("\n")

    # 교육시간 선택
    ampm_filter = input("## 교육시간 선택 (1: 오전, 2: 오후, 3: 전체): ")
    ampm_msg = ""
    if ampm_filter == "1":
        ampm_msg = "오전 "
    elif ampm_filter == "2":
        ampm_msg = "오후 "
    else:
        ampm_filter = None
        ampm_msg = ""
    print("\n")

    print(f"\n### {selected_sido[0]} 민방위({selected_year}년차) {ampm_msg}집합교육 일정 조회 (조회기간: {START_DATE:%Y-%m-%d} ~ {END_DATE:%Y-%m-%d}) ###", end="\n\n")
    for (sigungu_name, sigungu_code) in SIGUNGU_LIST:
        schedules = []
        for edu_target_code in EDU_TARGET_CODES:
            response = fetch_schedules(selected_sido[1], sigungu_code, edu_target_code, ampm_filter)
            schedules.extend(response)
        
        if schedules:
            for schedule in schedules:
                print(f"- [{sigungu_name}] {schedule['schedule']} @ {schedule['place']}")
        else:
            print(f"- [{sigungu_name}] 교육일정 없음.")
        print("\n")
    
    print("### 조회 완료 ###")
