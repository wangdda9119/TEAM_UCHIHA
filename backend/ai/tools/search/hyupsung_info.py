from langchain_core.tools import tool
import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
import re

urllib3.disable_warnings()

URL_MAP = {
    "동아리": "https://www.uhs.ac.kr/uhs/295/subview.do",
    "학생식단": "https://www.uhs.ac.kr/uhs/2951/subview.do",
    "교직원식단": "https://www.uhs.ac.kr/uhs/2949/subview.do",
    "등록금": "https://www.uhs.ac.kr/global/2697/subview.do",
    "교환학생": "https://www.uhs.ac.kr/global/2710/subview.do",
    "취업률": "https://www.academyinfo.go.kr/popup/pubinfo1690/list.do?schlId=0000207",
    "장학금 공지사항": "https://www.uhs.ac.kr/uhs/155/subview.do?enc=Zm5jdDF8QEB8JTJGcG9ydGFsQmJzJTJGdWhzJTJGNCUyRmxpc3QuZG8lM0ZzcmNoV3JkJTNEJUVDJTlFJUE1JUVEJTk1JTk5JUVBJUI4JTg4JTI2c3JjaENvbHVtbiUzRHNqJTI2cGFnZSUzRDIlMjY%3D#this",
    "공모전 공지사항": "https://www.uhs.ac.kr/uhs/155/subview.do?enc=Zm5jdDF8QEB8JTJGcG9ydGFsQmJzJTJGdWhzJTJGNCUyRmxpc3QuZG8lM0ZzcmNoV3JkJTNEJUVBJUIzJUI1JUVCJUFBJUE4JUVDJUEwJTg0JTI2c3JjaENvbHVtbiUzRHNqJTI2cGFnZSUzRDElMjY%3D"
}

KEYWORDS = {
    "학식": "학생식단",
    "학생 식당": "학생식단",
    "학생식당": "학생식단",
    "메뉴": "학생식단",
    "식단": "학생식단",
    "교직원 식당": "교직원식단",
    "취업": "취업률",
    "취업률": "취업률",
    "취업 정보": "취업률",
    "장학금": "장학금 공지사항",
    "장학금 공지": "장학금 공지사항",
    "장학금 공지사항": "장학금 공지사항",
    "공모전": "공모전 공지사항",
    "공모전 공지": "공모전 공지사항",
    "공모전 공지사항": "공모전 공지사항",
    "동아리": "동아리",
    "동아리 활동": "동아리",
    "동아리 모집": "동아리",
    "동아리 모집": "동아리",
    "동아리 모집": "동아리",

}


def _extract_day(query: str) -> str | None:
    """
    '14일', '13일' 같은 패턴에서 '14', '13'만 뽑아준다.
    """
    m = re.search(r"(\d{1,2})일", query)
    if m:
        return m.group(1)  # 예: '14'
    return None


@tool
def uhs_fetch_info(query: str) -> str:
    """협성대 식단·등록금·동아리 HTML을 가져와, 날짜가 들어있는 식단 행을 우선적으로 추출합니다."""

    # 1) 키워드 매핑 → 타겟 URL 결정
    target = None
    for k, v in KEYWORDS.items():
        if k in query:
            target = v
            break

    if not target:
        for key in URL_MAP.keys():
            if key in query:
                target = key
                break

    if not target:
        return "지원 항목: 동아리, 학생식단, 교직원식단, 등록금, 교환학생, 취업률"

    url = URL_MAP[target]
    logger.info(f"[uhs_fetch_info] target='{target}', url='{url}'")

    # 2) '14일' → '14' 형식으로 일(day)만 추출
    day_str = _extract_day(query)
    logger.info(f"[uhs_fetch_info] day_str={day_str}")

    # 3) HTML 요청
    try:
        resp = requests.get(url, timeout=8, verify=False)
        logger.info(f"[uhs_fetch_info] status_code={resp.status_code}")

        if resp.status_code != 200:
            return f"요청 실패: 상태 코드 {resp.status_code}"

        html = resp.text
        logger.info(f"[uhs_fetch_info] raw_html_snippet=\n{html[:800]}")
    except Exception as e:
        logger.error(f"[uhs_fetch_info] 요청 예외: {e}")
        return f"요청 실패: {e}"

    # 4) HTML 파싱
    try:
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table")
        logger.info(f"[uhs_fetch_info] table_count={len(tables)}")

        candidate_rows: list[str] = []

        # day_str가 있으면 그 날짜가 들어있는 행만 뽑는다
        day_pattern = None
        if day_str:
            # '2025.11.14 ( 금 )' 같은 패턴에서 '14' 부분을 잡기 위한 정규식
            # 예: '.14 (' 이런 부분을 노린다
            day_pattern = re.compile(rf"\.\s*0?{day_str}\s*\(")

        for t_idx, table in enumerate(tables):
            for tr in table.find_all("tr"):
                row_text = tr.get_text(" ", strip=True)
                if not row_text:
                    continue

                # 샘플 몇 줄 로그로 보기
                if len(candidate_rows) < 5:
                    logger.info(f"[uhs_fetch_info] sample_row[{t_idx}]: {row_text[:150]}")

                # 4-1) 날짜 지정된 경우: 날짜 패턴 매칭
                if day_pattern and day_pattern.search(row_text):
                    candidate_rows.append(row_text)
                # 4-2) 날짜 지정이 안 된 경우: '중식', '석식' 같은 키워드 포함 행만 수집
                elif not day_pattern and any(k in row_text for k in ["중식", "석식", "조식", "메뉴"]):
                    candidate_rows.append(row_text)

        # 5) 날짜 기반 식단 행 우선 반환
        if candidate_rows:
            logger.info(f"[uhs_fetch_info] found {len(candidate_rows)} candidate_rows")
            joined = "\n".join(candidate_rows)
            return f"[{target} 식단 추출 결과]\n\n{joined}"

        # 6) 후보 행이 하나도 없으면 전체 텍스트 일부 반환 (fallback)
        full_text = soup.get_text("\n", strip=True)
        logger.info(f"[uhs_fetch_info] fallback_full_text_snippet=\n{full_text[:800]}")
        return f"[{target} 전체 텍스트 일부]\n\n{full_text}"

    except Exception as e:
        logger.error(f"[uhs_fetch_info] HTML 파싱 예외: {e}")
        return f"HTML 파싱 오류: {e}"
