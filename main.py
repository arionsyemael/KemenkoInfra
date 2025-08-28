from scraper.fetcher import fetch_all_pages
from scraper.parser import parse_html
from scraper.saver import save_data
from datetime import datetime


def main():
    all_html = fetch_all_pages()
    all_data = []

    for html in all_html:
        if html:
            all_data.extend(parse_html(html))

    # Sorting berdasarkan tanggal (tanpa tahun, default tahun = 2025)
    def sort_key(item):
        try:
            return datetime.strptime(item["tanggal"], "%d %b")
        except:
            return datetime.min

    sorted_data = sorted(all_data, key=sort_key, reverse=True)

    save_data(sorted_data)
    print(f"[INFO] Scraping selesai. Total {len(sorted_data)} berita disimpan.")


if __name__ == "__main__":
    main()