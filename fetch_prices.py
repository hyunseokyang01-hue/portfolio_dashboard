"""
fetch_prices.py — index.html의 HOLDINGS에서 USD 종목을 읽어 Yahoo Finance(yfinance) 종가를 prices.json으로 저장.
GitHub Actions(.github/workflows/prices.yml)에서 평일 장 마감 후 실행. 브라우저는 Yahoo를 직접 못 부르므로(CORS) 이 파일을 거친다.
종목 실패는 1회 재시도 후 스킵 (semi-dashboard/run_semi.py와 같은 패턴).
"""
import json, re, time, datetime
import yfinance as yf

html = open("index.html", encoding="utf-8").read()
block = html[html.index("const HOLDINGS = ["):]
block = block[:block.index("];")]
tickers = sorted(set(re.findall(r'ticker:"([A-Z][A-Z0-9.\-]*)"[^}]*ccy:"USD"', block)))
print("tickers:", tickers)

def last_close(sym):
    h = yf.Ticker(sym).history(period="10d", auto_adjust=False)
    h = h.dropna(subset=["Close"])
    if h.empty:
        raise ValueError("no data")
    c = float(h["Close"].iloc[-1]); p = float(h["Close"].iloc[-2]) if len(h) > 1 else None
    return {"price": round(c, 4), "date": h.index[-1].strftime("%Y%m%d"), "chg": round((c / p - 1) * 100, 2) if p else None}

out = {"updatedAt": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "source": "Yahoo Finance via yfinance", "prices": {}, "failed": []}
for t in tickers + ["KRW=X"]:
    for attempt in range(2):
        try:
            out["prices"][t] = last_close(t); print(t, out["prices"][t]); break
        except Exception as e:
            if attempt == 0:
                time.sleep(3)
            else:
                out["failed"].append(t); print("[skip]", t, e)

json.dump(out, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
