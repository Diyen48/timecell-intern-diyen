import yfinance as yf
import requests
from datetime import datetime

def get_exchange_rate(from_currency, to_currency):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()

        return data["rates"][to_currency]

    except Exception as e:
        print(f"⚠️ Exchange rate error: {e}")
        return None
#Fetches price of a stock/index using yfinance.
def fetch_stock_price(ticker, display_name, currency):
    try:
        data = yf.Ticker(ticker)
        base_currency = data.fast_info.get("currency", "USD")
        price = data.fast_info["last_price"]
        if base_currency == currency:
            price = price
        else:
            rate = get_exchange_rate(base_currency, currency)
            price = price * rate if rate else "ERROR"

        return {"name": display_name, "price": round(price, 2), "currency": currency}
    except Exception as e:
        print(f"  ⚠️  Error fetching {display_name}: {e}")
        return {"name": display_name, "price": "ERROR", "currency": currency}

#Fetches crypto price from CoinGecko
def fetch_crypto_price(coin_id, display_name):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises error if status code is 4xx/5xx
        price = response.json()[coin_id]["usd"]
        return {"name": display_name, "price": round(price, 2), "currency": "USD"}
    except Exception as e:
        print(f"  ⚠️  Error fetching {display_name}: {e}")
        return {"name": display_name, "price": "ERROR", "currency": "USD"}


def print_table(assets):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    print(f"\n Asset Prices — fetched at {timestamp}\n")

    top    = "┌─────────────┬──────────────┬──────────┐"
    header = "│ Asset       │ Price        │ Currency │"
    mid    = "├─────────────┼──────────────┼──────────┤"
    bottom = "└─────────────┴──────────────┴──────────┘"

    print(top)
    print(header)
    print(mid)

    for asset in assets:
        name = asset["name"].ljust(11)
        price = str(asset["price"]).rjust(12)
        currency = asset["currency"].ljust(8)
        print(f"│ {name} │ {price} │ {currency} │")

    print(bottom)


if __name__ == "__main__":
    print("Fetching market data...\n")

    results = []

    # 1. NIFTY 50 (Indian stock index)
    results.append(fetch_stock_price("^NSEI", "NIFTY50", "INR"))

    # 2. Bitcoin (crypto)
    results.append(fetch_crypto_price("bitcoin", "BTC"))

    # 3. Ethereum (crypto)
    results.append(fetch_crypto_price("ethereum", "ETH"))

    print_table(results)