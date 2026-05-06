import yfinance as yf
from datetime import datetime, timedelta

# 애플 티커 생성
ticker = yf.Ticker("AAPL")

# 회사 정보 가져오기
info = ticker.info

# 출력할 정보
print("=" * 50)
print("회사 정보")
print("=" * 50)
print(f"회사명: {info.get('longName', 'N/A')}")
print(f"현재가: ${info.get('currentPrice', 'N/A'):,.2f}" if info.get('currentPrice') else "현재가: N/A")

# 전일 대비 등락률 계산
previous_close = info.get('previousClose', 0)
current_price = info.get('currentPrice', 0)
if previous_close and current_price:
    change_rate = ((current_price - previous_close) / previous_close) * 100
    print(f"전일 대비 등락률: {change_rate:.2f}%")
else:
    print("전일 대비 등락률: N/A")

print("\n" + "=" * 50)
print("최근 1개월 역사적 데이터 (처음 5개 행)")
print("=" * 50)

# 최근 1개월 데이터 가져오기
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

historical_data = ticker.history(start=start_date, end=end_date)
print(historical_data.head(5))
