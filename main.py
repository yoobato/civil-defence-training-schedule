import requests
from datetime import datetime, date

# 서울 지역 시군구 코드와 이름 매핑
REGION = {
    "3220000": "강남구",
    "3240000": "강동구",
    "3080000": "강북구",
    "3150000": "강서구",
    "3200000": "관악구",
    "3040000": "광진구",
    "3160000": "구로구",
    "3170000": "금천구",
    "3100000": "노원구",
    "3090000": "도봉구",
    "3050000": "동대문구",
    "3190000": "동작구",
    "3130000": "마포구",
    "3120000": "서대문구",
    "3210000": "서초구",
    "3030000": "성동구",
    "3070000": "성북구",
    "3230000": "송파구",
    "3140000": "양천구",
    "3180000": "영등포구",
    "3020000": "용산구",
    "3110000": "은평구",
    "3000000": "종로구",
    "3010000": "중구",
    "3060000": "중랑구",
}

DAY_OF_WEEK_KR = ["월", "화", "수", "목", "금", "토", "일"]

for code, name in REGION.items():
    educations = requests.get(f"https://www.safekorea.go.kr/idsiSFK/neo/ext/json/civilDefense/civilDefEduList/civilDefEduList_{code}.json").json()
    # {
    # "EDC_DE": "20250625",
    # "ROWCNT": 220,
    # "SGG_CD": "3220000",
    # "EDC_SE_CD": "10",
    # "EDC_SE_NM": "기본교육",
    # "EDCNTR_ADRES": "서울특별시 강남구 대치동 509-2 ",
    # "EDCNTR_RDNMADR": "서울특별시 강남구 삼성로 154 (대치동)",
    # "EDC_TGT_SE_CD": "31",
    # "EDC_TGT_SE_NM": "민방위대 편입 1~2년차 대원",
    # "EDC_END_TIME": "1800",
    # "CLNS_LRGE_SE_CD": "1",
    # "EDCNTR_NM": "논현2동_강남구민회관 대강당(2층 대강당)",
    # "HDAY_SE": "0",
    # "EDC_BEGIN_TIME": "1400",
    # "ORGNM": "서울특별시 강남구 논현2동",
    # "TELNO": "02-3423-5168",
    # "EMD_CD": "3220042"
    # },

    # 교육일자 기준으로 오름차순 정렬
    educations.sort(key=lambda x: x["EDC_DE"])

    education_final = set()

    # 민방위 2년차 / 금요일 오전 교육만 추출
    for education in educations:
        education_date = datetime.strptime(education.get("EDC_DE"), "%Y%m%d").date()
        if education_date < date.today() or education_date > date(2025, 12, 31):
            # 교육 일정이 오늘 이전이거나 2025년 12월 31일 이후인 경우 건너뜀. ([오늘, 2025-12-31] 범위 내의 일정만 사용)
            continue

        if education.get("HDAY_SE") != "0":
            # 평일교육이 아닌 경우 건너뜀.
            continue

        # 31 : 민방위대 편입 1~2년차 대원, 33 : 민방위대 편입 2년차 대원
        if education.get("EDC_TGT_SE_CD") != "31" and education.get("EDC_TGT_SE_CD") != "33":
            # 교육대상이 아닌 경우 건너뜀.
            continue

        if education.get("EDC_BEGIN_TIME") != "0900":
            # 오전 교육이 아닌경우 건너뜀.
            continue

        # 요일
        day_of_week = ["월", "화", "수", "목", "금", "토", "일"][education_date.weekday()]
        if day_of_week != "금":
            # 금요일 교육이 아닌경우 건너뜀.
            continue

        # 최종후보
        education_final.add(frozenset({
            "datetime": f"{education_date.strftime('%Y-%m-%d')}({day_of_week}) {education.get('EDC_BEGIN_TIME')}-{education.get('EDC_END_TIME')}",
            "location": f"{education.get('EDCNTR_NM').split('_', 1)[1]}",
            "target": education.get('EDC_TGT_SE_NM')
        }.items()))
    
    if not education_final:
        # 유효한 교육 일정이 없는 경우 건너뜀.
        continue

    print(f"=== {name} 지역 민방위 교육 일정 ===")
    for education in education_final:
        edu = dict(education)
        print(f"{edu.get('datetime')} / {edu.get('location')} / {edu.get('target')}")
    print("\n")
