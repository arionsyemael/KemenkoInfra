import requests
from config.settings import BASE_URL, HEADERS

def fetch_all_pages():
    html_pages = []
    i = 0
    while True:
        if i == 0:
            url = BASE_URL
        else:
            url = f"{BASE_URL}/{i * 10}?"

        print(f"[INFO] Fetching page {i + 1}: {url}")
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            if '<article' not in response.text:
                print(f"[INFO] Tidak ada artikel lagi di halaman {i + 1}, berhenti.")
                break

            html_pages.append(response.text)
            i += 1
        except requests.RequestException as e:
            print(f"[ERROR] Gagal fetch {url}: {e}")
            break

    return html_pages
