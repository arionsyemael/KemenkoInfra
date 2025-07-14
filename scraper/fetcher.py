import requests
from config.settings import BASE_URL, HEADERS

def fetch_html():
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Gagal fetch halaman: {e}")
        return None
