# portfolio_dashboard

미국 반도체 · 한온시스템 · 현금흐름 통합 포트폴리오 대시보드 (GitHub Pages).

## 상시 갱신 방식
페이지를 열 때마다 브라우저가 아래 세 소스를 직접 읽어 다시 계산한다. 별도 빌드·배포 없음.

| 소스 | 주기 | 쓰는 값 |
| --- | --- | --- |
| KRX 대시보드 `krx-dashboard/kospi.html` | 일간 | 한온시스템·한국토지신탁 종가(FLOG), 연기금 LOG, 외국인·공매도 |
| 반도체 대시보드 `semi-dashboard/data.json` | 주간 (월) | INTC·MU 시세, 시나리오 확률, 사이클 신호, Intel 시나리오 |
| 매크로 브리핑 구글시트 (CALENDAR_30, ANALYSIS) | 일간 | USD/KRW, 반도체 지수, 나스닥, 코스피, 미 10년물, 분석 텍스트 |
| `prices.json` (이 저장소, GitHub Actions `prices.yml`) | 평일 05:30 KST | HOLDINGS의 모든 미국 종목 종가 (Yahoo Finance via yfinance) |

종목별로 위 소스 중 **가장 최신 날짜의 시세**를 쓴다. HOLDINGS에 미국 종목을 추가하면 다음 실행부터 자동으로 시세를 받는다(index.html 수정 시 즉시 1회 실행).

## 사람이 고치는 부분 (index.html 상단)
- `HOLDINGS` — 보유 종목·수량·평단. 체결 후 갱신. `manualPrice`/`manualDate`는 자동 시세가 모두 실패할 때만 쓰는 대체값
- `CASH` / `TRADES` — 현금, 체결 기록
- `CONFIG.rules` — 종목 상한·현금 비중·손절·서킷브레이커. 바꾸면 `RULE_LOG`에 사유 기록
- `CONFIG.hanonTriggers.q3Status` — 11/5 실적 후 `pass`/`fail`
- `EVENTS` — 일정
