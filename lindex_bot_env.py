import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

URL = "https://www.lindex.com/cz/outlet/miminko?hl=cs&page=1"
CHECK_INTERVAL = 180  # kontrola každé 3 minuty

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

previous_products = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def get_products():
    products = set()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # počkej 5 s, aby se načetly produkty
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    for item in soup.find_all("a"):
        href = item.get("href")
        if href and "/p/" in href:
            products.add("https://www.lindex.com" + href)
    return products

while True:
    try:
        # časová značka pro log
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