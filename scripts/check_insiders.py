import requests
import json
import os
from datetime import datetime

API_KEY = os.environ.get("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/stock/insider-transactions"

# tickers.txt ahora está en la raíz del proyecto
TICKERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tickers.txt")
NOTIFIED_FILE = os.path.join(os.path.dirname(__file__), "..", "notified_insiders.json")


def load_tickers():
    with open(TICKERS_FILE, "r") as f:
        tickers = [line.strip() for line in f.readlines() if line.strip()]
    return tickers


def load_notified():
    if not os.path.exists(NOTIFIED_FILE):
        return {}
    with open(NOTIFIED_FILE, "r") as f:
        return json.load(f)


def save_notified(data):
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(data, f, indent=4)


def fetch_insider_activity(symbol):
    params = {"symbol": symbol, "token": API_KEY}
    try:
        r = requests.get(BASE_URL, params=params)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Error consultando insiders de {symbol}: {e}")
        return None


def main():
    tickers = load_tickers()
    notified = load_notified()
    print(f"[{datetime.utcnow()}] 🔎 Comprobando insider trading...")

    for ticker in tickers:
        print(f"\n--- {ticker} ---")
        data = fetch_insider_activity(ticker)

        if not data or "data" not in data:
            continue

        new_buys = []

        for op in data["data"]:
            if op["transactionCode"] != "P":  # "P" = Purchase
                continue

            key = f"{ticker}-{op['filingDate']}-{op['name']}"
            if key not in notified:
                new_buys.append(op)
                notified[key] = True

        if new_buys:
            print(f"🟢 NUEVAS COMPRAS DE INSIDERS EN {ticker}:")
            for op in new_buys:
                print(f"  - {op['name']} compró {op['transactionShares']} acciones el {op['transactionDate']}")
        else:
            print("No hay nuevas compras.")

    save_notified(notified)
    print("\n✔ Finalizado.")


if __name__ == "__main__":
    main()
