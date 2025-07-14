import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import fetch_html
from scraper.parser import parse_html
from scraper.saver import save_data

def main():
    html = fetch_html()
    if html:
        berita = parse_html(html)
        save_data(berita)
        print(f"[INFO] Berhasil scraping {len(berita)} berita.")
    else:
        print("[ERROR] Gagal mengambil HTML.")

if __name__ == "__main__":
    main()
