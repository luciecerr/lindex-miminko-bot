import time
import os
import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

# Telegram token a chat ID z Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Interval kontroly v sekundách
CHECK_INTERVAL = 300  # 5 minut, můžeš změnit na 180 pro 3 minuty

# URL výprodeje
URL = "https://www.lindex.com/cz/outlet/miminko?hl=cs&page=1"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chyba při odesílání Telegram zprávy: {e}")

def get_products():
    products = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        # počká až se produkty načtou, max 15s
        page.wait_for_selector("div.product-tile", timeout=15000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        # najde všechny produkty
        for item in soup.find_all("div", class_="product-tile"):
            a_tag = item.find("a")
            if a_tag:
                href = a_tag.get("href")
                products.add("https://www.lindex.com" + href)
        browser.close()
    return products

previous_products = set()

while True:
    try:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now}] Kontrola Lindex Miminko výprodeje…")
        current_products = get_products()
        new_products = current_products - previous_products

        if previous_products and new_products:
            for prod in new_products:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{now}] Nalezen nový produkt: {prod}")
                send_telegram(f"👶 Nový produkt v Lindex Miminko výprodeji!\n{prod}")

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now}] Kontrola hotova, nalezeno {len(current_products)} produktů")
        previous_products = current_products

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{now}] Chyba: {e}")
        send_telegram(f"❌ Chyba při hlídání: {e}")
        time.sleep(CHECK_INTERVAL)