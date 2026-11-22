"""dart_watch.py — 보유 종목 DART 신규 공시 감시 (GitHub Actions)
- OpenDART list.json 으로 최근 7일 공시 조회 → dart_seen.json 에 없는 접수번호만 알림
- 알림 = GitHub Issue (라벨 dart). 저장소 Watch 설정에 따라 메일·앱 알림
- API 키는 저장소 Secret DART_API_KEY (코드·레포에 키를 두지 않음)
- 첫 실행은 기존 공시를 '본 것'으로만 기록하고 알림하지 않음
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

WATCH = {"00161125": "한온시스템(018880)"}   # DART corp_code → 표시명
IMPORTANT = ["대량보유", "최대주주", "주요사항", "분기보고서", "반기보고서", "사업보고서", "잠정",
             "단일판매", "공급계약", "증권발행실적", "풋옵션", "자기주식", "유상증자", "합병", "소송",
             "타법인", "기업설명회", "현금ㆍ현물배당", "주식등의"]
SEEN = "dart_seen.json"
KEY = os.environ.get("DART_API_KEY", "").strip()


def fetch(corp):
    end = datetime.date.today()
    q = urllib.parse.urlencode({"crtfc_key": KEY, "corp_code": corp,
                                "bgn_de": (end - datetime.timedelta(days=7)).strftime("%Y%m%d"),
                                "end_de": end.strftime("%Y%m%d"), "page_count": 100})
    with urllib.request.urlopen(f"https://opendart.fss.or.kr/api/list.json?{q}", timeout=30) as r:
        d = json.load(r)
    if d.get("status") not in ("000", "013"):     # 013 = 조회 결과 없음
        raise RuntimeError(f"DART 오류 {d.get('status')}: {d.get('message')}")
    return d.get("list", [])


def main():
    if not KEY:
        print("DART_API_KEY Secret 없음 — 건너뜀 (Settings > Secrets and variables > Actions)")
        return 0
    seen = json.load(open(SEEN, encoding="utf-8")) if os.path.exists(SEEN) else {}
    first_run = not seen
    new = []
    for corp, name in WATCH.items():
        ids = set(seen.get(corp, []))
        for it in fetch(corp):
            if it["rcept_no"] not in ids:
                ids.add(it["rcept_no"])
                new.append((name, it))
        seen[corp] = sorted(ids)[-300:]
    json.dump(seen, open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if first_run or not new:
        print(f"{'첫 실행 — 기록만' if first_run else '신규 공시 없음'} ({len(new)}건)")
        open("dart_alert.md", "w").close()
        return 0

    new.sort(key=lambda x: x[1]["rcept_no"])
    lines, hot = [], 0
    for name, it in new:
        imp = any(k in it["report_nm"] for k in IMPORTANT)
        hot += imp
        lines.append(f"- {'**[주요]** ' if imp else ''}{name} | {it['rcept_dt']} | {it['report_nm'].strip()} "
                     f"| 제출: {it['flr_nm']} | [원문](https://dart.fss.or.kr/dsaf001/main.do?rcpNo={it['rcept_no']})")
    title = f"[DART] 신규 공시 {len(new)}건{f' (주요 {hot})' if hot else ''} — {datetime.date.today():%Y-%m-%d}"
    with open("dart_alert.md", "w", encoding="utf-8") as f:
        f.write(title + "\n" + "\n".join(lines) + "\n")
    print(title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
