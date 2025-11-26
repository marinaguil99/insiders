from datetime import datetime

# --- Comprobar insiders ---
def check_symbol(symbol, notified):
    try:
        data = client.stock_insider_transactions(symbol)
    except Exception as e:
        print(f"❌ Error consultando {symbol}: {e}")
        return notified

    transactions = data.get("data", [])
    new_events = []

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    for t in transactions:
        # Filtrar solo compras/ventas
        if t["transactionCode"] not in ["P", "S"]:
            continue

        # Filtrar solo transacciones del mes actual
        try:
            t_date = datetime.strptime(t["filingDate"], "%Y-%m-%d")
        except Exception as e:
            print(f"❌ Error parseando fecha {t.get('filingDate')}: {e}")
            continue

        if t_date.year != current_year or t_date.month != current_month:
            continue  # Saltar transacciones de otros meses

        event_id = f"{t['symbol']}-{t['filingDate']}-{t['name']}-{t['transactionCode']}"
        if event_id not in notified:
            new_events.append(t)
            notified[event_id] = True

    if new_events:
        print(f"🟢 Nuevas transacciones de insiders en {symbol}: {len(new_events)}")
        html = format_email(new_events, symbol)
        send_email(f"Insider Alert: {symbol}", html)

    return notified
