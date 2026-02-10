import finnhub
import json
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

now = datetime.now()
current_year = now.year
current_month = now.month

# --- Variables de entorno ---
FINNHUB_KEY = os.environ.get("FINNHUB_KEY")
SENDGRID_KEY = os.environ.get("SENDGRID_KEY")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = os.environ.get("EMAIL_TO")

# --- Archivos ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TICKERS_FILE = os.path.join(BASE_DIR, "tickers1.txt")
NOTIFIED_FILE = os.path.join(BASE_DIR, "notified_insiders.json")
INSIDERS_FILE = os.path.join(BASE_DIR, "insiders.json")

# --- Inicialización Finnhub ---
client = finnhub.Client(api_key=FINNHUB_KEY)

# --- Obtiene el role del insider ---
def get_role(name):
    if not os.path.exists(INSIDERS_FILE):
        return None

    with open(INSIDERS_FILE, "r") as f:
        data = json.load(f)

    return data.get(name)

# --- Cargar tickers ---
def load_tickers():
    with open(TICKERS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

# --- Cargar historial de notificaciones ---
def load_notified():
    if os.path.exists(NOTIFIED_FILE):
        with open(NOTIFIED_FILE, "r") as f:
            return json.load(f)
    return {}

def save_notified(data):
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Enviar email ---
def send_email(subject, content):
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=EMAIL_TO,
        subject=subject,
        html_content=content
    )
    sg = SendGridAPIClient(SENDGRID_KEY)
    sg.send(message)

# --- Formatear contenido del email ---
def format_email(events, symbol):
    html = f"<h2>🔔 Nuevas transacciones de insiders en {symbol}</h2>"

    for e in events:
        position = get_role(e.get('name'))
        tipo = "Compra" if e.get('transactionCode') == "P" else "Venta"

        html += f"""
        <p>
        <b>Nombre:</b> {e.get('name')}<br>
        <b>Cargo:</b> {position}<br>
        <b>Fecha transacción:</b> {e.get('transactionDate')}<br>
        <b>Fecha reporte:</b> {e.get('filingDate')}<br>
        <b>Tipo:</b> {tipo}<br>
        <b>Acciones:</b> {e.get('transactionShares')}<br>
        <b>Precio:</b> {e.get('transactionPrice')}<br>
        </p><hr>
        """
    return html

# --- Comprobar insiders ---
def check_symbol(symbol, notified):
    try:
        data = client.stock_insider_transactions(symbol)
    except Exception as e:
        print(f"❌ Error consultando {symbol}: {e}")
        return notified

    transactions = data.get("data", [])
    new_events = []

    for t in transactions:
        if t.get("transactionCode") not in ["P", "S"]:
            continue

        # Usar la fecha REAL de la transacción
        t_date_str = t.get('transactionDate')
        if not t_date_str:
            continue

        t_date = datetime.strptime(t_date_str, "%Y-%m-%d")

        # Solo transacciones del mes actual
        if t_date.year != current_year or t_date.month != current_month:
            continue

        # ID único REAL (evita duplicados el mismo día)
        event_id = f"{t['symbol']}-{t['transactionDate']}-{t['name']}-{t['transactionShares']}-{t['transactionPrice']}"

        if event_id not in notified:
            new_events.append(t)
            notified[event_id] = True

    if new_events:
        print(f"🟢 Nuevas transacciones de insiders en {symbol}: {len(new_events)}")
        html = format_email(new_events, symbol)
        send_email(f"Insider Alert: {symbol}", html)

    return notified

# --- Main ---
if __name__ == "__main__":
    tickers = load_tickers()
    notified = load_notified()
    total_new = 0

    for sym in tickers:
        before = len(notified)
        notified = check_symbol(sym, notified)
        total_new += len(notified) - before

    if total_new == 0:
        print("No hay nuevas transacciones de insiders este mes.")
    else:
        print(f"✔ Total nuevas transacciones enviadas: {total_new}")

    save_notified(notified)
