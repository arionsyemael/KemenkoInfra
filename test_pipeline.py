import os
import sys
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pytrends.request import TrendReq
import pandas as pd
import time
import nltk
from nltk.util import ngrams

# Fix the path handling
current_dir = os.path.dirname(os.path.abspath(__file__))
SCRAPING_PATH = os.path.join(current_dir, "Scraping")

# Add Scraping root directory to Python path
if SCRAPING_PATH not in sys.path:
    sys.path.insert(0, SCRAPING_PATH)

# Now import after path is set
from scraper.fetcher import fetch_all_pages

# Add headers for web scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


def clean_keywords(titles):
    """Extract and clean keywords from titles"""
    stopwords = set(
        [
            "dan",
            "untuk",
            "dengan",
            "di",
            "ke",
            "pada",
            "yang",
            "dalam",
            "oleh",
            "atau",
            "adalah",
            "ini",
            "itu",
            "untuk",
            "juga",
            "masa",
            "masa depan",
        ]
    )

    important_phrases = {
        "kemenko infra",
        "menko infrastruktur",
        "pembangunan infrastruktur",
        "infrastruktur nasional",
        "koordinasi pembangunan",
        "ahy",
        "seawall",
        "sea wall",
        "tanggul laut",
        "menko ahy",
        "tata ruang",
        "menko ahy indonesia",
        "nasional menko ahy tekankan",
        "presiden prabowo menko ahy",
        "ahy hadiri rapat terbatas",
        "infrastruktur indonesia",
        "resmikan stadion",
        "tata ruang terpadu",
        "banggar dpr ri",
        "pelantikan kepala daerah",
        "kerja sama infrastruktur",
        "atr bpn",
        "tegaskan infrastruktur",
        "prioritas infrastruktur transportasi lebaran",
        "indonesia maju",
        "lepas tim mudik",
        "utara jakarta",
        "saat lebaran menko ahy",
        "menko pmk",
        "bersama menko",
        "penurunan tiket pesawat",
        "tekankan pentingnya infrastruktur",
        "inews media",
        "pentingnya infrastruktur pendidikan",
        "prabowo menko",
        "presiden bahas",
        "hanya fisik tapi",
        "harga tiket pesawat",
        "infrastruktur jadi",
        "menko ahy pembangunan infrastruktur",
        "pacitan menko ahy",
        "sesuai arahan presiden",
        "rakor terkait",
        "menko ahy soroti",
        "lakukan aksi cepat",
        "menko ahy generasi muda",
        "taruna nusantara",
        "arus mudik",
        "pembangunan kewilayahan",
        "menko ahy optimalkan perencanaan",
        "pastikan kesiapan infrastruktur",
        "menko ahy komitmen",
        "dunia menko",
        "aksi cepat",
        "tegaskan pemerintah",
        "ahy ajak",
        "akan gelar",
        "nataru menko ahy",
        "halal bihalal",
        "nusantara menko ahy",
        "infrastruktur harus",
        "ahy komitmen",
        "apresiasi kinerja",
        "kolaborasi global",
        "fisik tapi",
        "ahy kita",
        "infrastruktur nasional",
        "perkuat kemitraan strategis",
        "dunia menko ahy",
        "menko ahy tegaskan pentingnya",
        "road to",
        "indonesia siap",
        "pembangunan infrastruktur",
        "semangat kebersamaan",
        "dampak ekonomi",
        "perkuat kemitraan",
        "pacitan menko",
        "kepastian hukum",
        "lepas tim liputan mudik",
        "menko ahy jadi",
        "menko ahy ingatkan pentingnya",
        "banggar dpr ri menko",
        "ahy siap",
        "pembangunan infrastruktur harus",
        "ahy program",
        "menko ahy kemitraan",
        "infrastruktur menko ahy",
        "kabinet merah putih",
        "aksi cepat tanggap darurat",
        "menko ahy ajak wujudkan",
        "daerah menko ahy",
        "menko ahy bahas",
        "menko infrastruktur",
        "investasi pembangunan",
        "ahy prioritaskan program",
        "pembangunan infrastruktur menko",
        "bermanfaat bagi",
        "pmk pratikno",
        "menuju indonesia emas",
        "ahy tegaskan infrastruktur",
        "jalan menko ahy prioritaskan",
        "lintas kementerian",
        "ahy pemerintah",
        "ahy sinergi",
        "bersama presiden prabowo",
        "ri menko",
        "menko ahy siap bersinergi",
        "ahy pastikan kesiapan",
        "tekankan pentingnya",
        "transportasi lebaran",
        "jajaran kemenko",
        "brics menko ahy",
        "giant sea",
        "layani masyarakat",
        "pembangunan ikn",
        "menko ahy tegaskan komitmen",
        "stanford menko ahy",
        "ahy jadi",
        "tiket pesawat",
        "dunia pendidikan",
        "berikan pidato",
        "forum ekonomi terbesar",
        "infrastruktur berkelanjutan",
        "harga tiket",
        "ahy perkuat",
        "kolaborasi strategis",
        "banggar dpr",
        "ahy pembangunan infrastruktur harus",
        "dorong pembangunan",
        "conference on infrastructure",
        "serahkan sertifikat",
        "menko ahy optimalkan",
        "serahkan sertifikat tanah",
        "sma taruna nusantara menko",
        "menko ahy hadiri rapat",
        "kemenko infra menko",
        "prioritas infrastruktur",
        "berikan pidato kunci",
        "infrastruktur pendidikan",
        "pejabat kemenko infra",
        "sekolah rakyat",
        "ri menko ahy",
        "kunjungi bendungan",
        "prioritaskan program",
        "menko ahy harap",
        "pertumbuhan ekonomi",
        "jalan menko",
        "pimpin rakor persiapan",
        "infrastruktur jadi fondasi",
        "tegaskan pemerintah lakukan",
        "nusantara menko",
        "ahy bahas",
        "aksi cepat tanggap",
        "dukung pembangunan",
        "tetap jalan menko ahy",
        "ahy dorong",
        "bahas potensi",
        "ahy ingatkan pentingnya",
        "tetap jalan",
        "kuliah umum",
        "jajaran kemenko infra",
        "ahy pembangunan infrastruktur",
        "pantai utara",
        "dpr ri menko ahy",
        "tim mudik",
        "mendorong pertumbuhan",
        "taruna nusantara menko ahy",
        "jadi pembicara kunci",
        "prabowo menko ahy",
        "bahas prioritas infrastruktur transportasi",
        "ici menteri",
        "kemitraan strategis",
        "tegaskan pentingnya infrastruktur",
        "hari kedua",
        "ahy tegaskan pemerintah lakukan",
        "pembangunan berkelanjutan",
        "tinjau sekolah rakyat",
        "international conference on",
        "menko ahy sampaikan",
        "mudik lebaran menko",
        "menko ahy kita",
        "bersama kepala daerah se",
        "pesisir utara jawa",
        "giant sea wall",
        "bersama presiden prabowo menko",
        "presiden bahas prioritas infrastruktur",
        "pemerataan pembangunan",
        "jadi fondasi",
        "bukti kehadiran negara",
        "media group",
        "tol semarang demak",
        "kehadiran negara",
        "tim liputan mudik",
        "menko ahy tekankan",
        "asta cita presiden prabowo",
        "ekonomi berkelanjutan",
        "stanford menko",
        "fondasi pembangunan",
        "bank dunia",
        "infra menko",
        "perjalanan masyarakat",
        "langsung banjir",
        "pimpin rakor",
        "kolaborasi pemerintah",
        "keterbukaan informasi",
        "komitmen infrastruktur",
        "kebijakan tata ruang",
        "ahy pembangunan",
        "ekonomi terbesar",
        "nasional menko ahy",
        "pemerintah lakukan aksi cepat",
        "pu menko",
        "menko ahy sinergi",
        "sma taruna nusantara",
        "presiden prabowo subianto",
        "potensi ekonomi",
        "to ici",
        "bahas potensi kolaborasi",
        "ajak investor",
        "arahan presiden prabowo menko",
        "bagi rakyat",
        "infrastruktur transportasi",
        "kemenko infra",
        "konferensi internasional infrastruktur",
        "international conference",
        "kebijakan tata",
        "pembangunan infrastruktur nasional",
        "pejabat kemenko",
        "bangun indonesia",
        "ahy paparkan",
        "resmikan terminal",
        "siap bersinergi",
        "daerah se",
        "ahy optimalkan",
        "rapat terbatas",
        "cek langsung banjir",
        "pastikan pembangunan infrastruktur tetap",
        "bahas prioritas infrastruktur",
        "ahy generasi",
        "strategis presiden",
        "menko ahy generasi",
        "tegaskan pemerintah lakukan aksi",
        "dorong pertumbuhan ekonomi",
        "nataru menko",
        "fondasi pertumbuhan",
        "menko ahy tegaskan pemerintah",
        "ahy pastikan",
        "indonesia emas",
        "sertifikat tanah",
        "pengelolaan sampah",
        "inews media group menko",
        "menko ahy gelar",
        "ahy ingatkan pentingnya kerja",
        "forum ici",
        "tiongkok menko ahy",
        "jalan menko ahy",
        "conference on",
        "asia menko ahy",
        "bahas pembangunan",
        "lepas tim",
        "ruang terpadu",
        "ici menko",
        "menko ahy pemerintah siapkan",
        "saat lebaran menko",
        "berikan kuliah umum",
        "hadiri ici",
        "keadilan sosial",
        "prabowo subianto",
        "infrastruktur dukung",
        "ingatkan pentingnya",
        "merah putih",
        "ahy tegaskan pentingnya",
        "ahy soroti",
        "menko ahy tegaskan",
        "resmikan gedung",
        "potensi kolaborasi",
        "ahy apresiasi",
        "dampingi presiden resmikan",
        "ahy harus",
        "selama nataru",
        "ici menko ahy",
        "ahy gelar",
        "pejabat kemenko infra menko",
        "prioritas pembangunan",
        "sesuai arahan presiden prabowo",
        "road to ici menko",
        "ahy harap",
        "menko ahy hadiri",
        "ahy sampaikan",
        "kerja sama",
        "bersama menko pmk",
        "prioritaskan program bermanfaat",
        "menko ahy pembangunan",
        "asta cita",
        "lakukan aksi",
        "generasi muda",
        "jadi pembicara",
        "bertemu menteri",
        "menko ahy ajak",
        "kemenko infra menko ahy",
        "media group menko ahy",
        "ketahanan pangan",
        "menko ahy infrastruktur",
        "transportasi nasional",
        "bank dunia menko",
        "ahy kemitraan",
        "pembangunan nasional",
        "presiden resmikan",
        "infrastruktur pengelolaan",
        "ingatkan pentingnya kerja sama",
        "bermanfaat bagi rakyat",
        "menko ahy tekankan pentingnya",
        "asia menko",
        "potensi ekonomi kreatif",
        "ekonomi kreatif",
        "menko ahy tegaskan infrastruktur",
        "menko pmk pratikno",
        "bekasi menko ahy",
        "bekasi menko ahy tegaskan",
        "menko ahy apresiasi",
        "menko ahy dorong kolaborasi",
        "wakili indonesia",
        "tantangan pembangunan infrastruktur",
        "daerah menko",
        "dampingi presiden prabowo",
        "dorong kolaborasi",
        "group menko ahy",
        "sesuai arahan",
        "tim liputan",
        "wujudkan asta cita",
        "ahy tegaskan komitmen",
        "road to ici",
        "ahy cek",
        "ahy infrastruktur",
        "program bermanfaat",
        "infrastruktur tetap",
        "lebaran h",
        "kepala daerah menko",
        "pelantikan kepala daerah menko",
        "ahy tegaskan pentingnya infrastruktur",
        "infrastruktur transportasi lebaran",
        "bukan hanya",
        "infrastruktur tangguh",
        "menko infra",
        "rakor persiapan",
        "dorong pertumbuhan",
        "kepala daerah",
        "program bermanfaat bagi rakyat",
        "cek langsung",
        "menko ahy pastikan",
        "perkuat kerja sama",
        "bahas prioritas",
        "pastikan pembangunan infrastruktur",
        "pastikan pembangunan",
        "menko ahy pemerintah",
        "kunjungi kementerian",
        "pembicara kunci",
        "bersama kepala daerah",
        "perencanaan infrastruktur",
        "hadiri rapat terbatas",
        "tegaskan komitmen",
        "ahy gelar rakor",
        "pembangunan infrastruktur tetap",
        "diresmikan menko",
        "ahy wujud",
        "tekankan kolaborasi",
        "menko ahy perkuat",
        "strategis nasional",
        "idul fitri",
        "pembangunan indonesia",
        "perkuat kerja",
        "menko ahy cek",
        "proyek strategis",
        "menko ahy dorong",
        "presiden prabowo",
        "ahy hadiri rapat",
        "pentingnya infrastruktur",
        "menko ahy program",
        "kunci ketahanan",
        "program strategis",
        "forum ekonomi",
        "kinerja menko ahy",
        "ipdn menko ahy",
        "rakor bersama",
        "pemerintah lakukan",
        "infrastruktur tetap jalan",
        "cepat tanggap darurat",
        "rempang menko",
        "donggala menko ahy",
        "ahy dorong kolaborasi",
        "lakukan aksi cepat tanggap",
        "arahan presiden prabowo",
        "taruna nusantara menko",
        "pidato kunci",
        "daerah menko ahy siap",
        "bukti kehadiran",
        "ahy hadiri",
        "kunci ketahanan pangan",
        "menko ahy prioritaskan",
        "presiden resmikan stadion",
        "cita presiden",
        "antar wilayah",
        "pentingnya kerja",
        "penurunan tiket",
        "menko ahy harus",
        "konferensi internasional infrastruktur menko",
        "bank dunia menko ahy",
        "sea wall",
        "arahan presiden",
        "prioritas infrastruktur transportasi",
        "dorong percepatan",
        "menko ahy prioritaskan program",
        "bendungan karian",
        "ahy prioritaskan",
        "menko ahy",
        "tidak hanya",
        "lebaran menko ahy",
        "semarang demak",
        "konferensi internasional",
        "infrastruktur menko",
        "tantangan pembangunan",
        "ahy pemerintah siapkan",
        "ici infrastruktur",
        "tanggap darurat",
        "to ici menko",
        "pertahanan negara",
        "mudik lebaran",
        "soroti pentingnya",
        "tol semarang",
        "jadi mitra",
        "hanya fisik",
        "media group menko",
        "internasional infrastruktur menko ahy",
        "jalan tol",
        "liputan mudik",
        "kementerian lembaga",
        "ajak wujudkan",
        "cita presiden prabowo",
        "dorong inovasi",
        "international conference on infrastructure",
        "pembangunan infrastruktur tetap jalan",
        "donggala menko",
        "ahy tegaskan",
        "kinerja menko",
        "sama infrastruktur",
        "pentingnya kerja sama",
        "pesisir utara",
        "kepala daerah menko ahy",
        "ahy ajak wujudkan",
        "tinjau pelabuhan",
        "pastikan kesiapan",
        "infrastruktur tetap jalan menko",
        "bersama kepala",
        "kolaborasi bangun",
        "mudik lebaran menko ahy",
        "menko ahy soroti pentingnya",
        "menko infrastruktur ahy",
        "lebih terhubung",
        "pemerintah siapkan",
        "hadiri rapat",
        "ahy tekankan pentingnya infrastruktur",
        "ahy tekankan pentingnya",
        "ahy prioritaskan program bermanfaat",
        "ingatkan pentingnya kerja",
        "ahy soroti pentingnya",
        "bangun infrastruktur",
        "menko ahy gelar rakor",
        "ici menlu sugiono",
        "tinjau sekolah",
        "pemerintahan prabowo",
        "prabowo menko ahy kita",
        "rapat bersama",
        "menko ahy paparkan",
        "prioritaskan program bermanfaat bagi",
        "ahy ingatkan",
        "dpr ri",
        "ici menlu",
        "menko ahy ingatkan",
        "mudik lebaran h",
        "pu menko ahy",
        "ipdn menko",
        "berikan kuliah",
        "dpr ri menko",
        "kepala daerah se",
        "pemerintah lakukan aksi",
        "gelar rakor",
        "ahy tekankan",
        "cek kesiapan",
        "sdm unggul",
        "group menko",
        "utara jawa",
        "bersama presiden",
        "masa depan",
        "pelantikan kepala",
        "ahy optimalkan perencanaan",
        "lantik pejabat",
        "diresmikan menko ahy",
        "lepas tim liputan",
        "inews media group",
        "program bermanfaat bagi",
        "on infrastructure",
        "to ici menko ahy",
        "brics menko",
        "menuju indonesia",
        "maksimalkan utilisasi",
        "ahy indonesia",
        "menko ahy siap",
        "arus mudik lebaran",
        "kabinet merah",
        "dampingi presiden",
        "tetap jalan menko",
        "kebijakan tata ruang terpadu",
        "menko ahy wujud",
        "menlu sugiono",
        "saat lebaran",
        "strategis presiden prabowo",
        "mitra internasional",
        "tiongkok menko",
        "pantai utara jakarta",
        "optimalkan perencanaan",
        "kesiapan infrastruktur",
        "wujudkan asta",
        "presiden prabowo menko",
        "nasional menko",
        "asta cita presiden",
        "optimalkan perencanaan infrastruktur",
        "siapkan kebijakan",
        "infra menko ahy",
        "menteri pu",
        "internasional infrastruktur menko",
        "forum brics",
        "presiden bahas prioritas",
        "lebih baik",
        "luar negeri",
        "ici wamen",
        "tegaskan pentingnya",
        "lebaran menko",
        "cepat tanggap",
        "rempang menko ahy",
        "ahy tegaskan pemerintah",
        "kesejahteraan masyarakat",
        "pastikan perjalanan",
        "pembangunan infrastruktur menko ahy",
        "bekasi menko",
        "internasional infrastruktur",
        "pembangunan infrastruktur indonesia",
        "sma taruna",
        "ahy optimalkan perencanaan infrastruktur",
        "ahy generasi muda",
        "menko ahy pastikan kesiapan",
        "ahy siap bersinergi",
        "infrastruktur ahy",
    }

    phrases = set()
    for title in titles:
        words = title.lower().split()
        # Extract 2-3 word phrases
        for i in range(len(words) - 1):
            phrase = " ".join(words[i : i + 2])
            if not any(w in stopwords for w in phrase.split()):
                phrases.add(phrase)
            if i < len(words) - 2:
                phrase = " ".join(words[i : i + 3])
                if not any(w in stopwords for w in phrase.split()):
                    phrases.add(phrase)

    phrases.update(important_phrases)
    return list(phrases)


def get_trends_data(phrases, timeframe="today 3-m"):
    """Get Google Trends data"""
    print("Getting trends data...")
    pytrends = TrendReq(hl="id-ID", tz=420)
    results = {}

    for i in range(0, len(phrases), 5):
        batch = phrases[i : i + 5]
        try:
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo="ID")
            data = pytrends.interest_over_time()

            for phrase in batch:
                if phrase in data.columns:
                    results[phrase] = {
                        "trend_data": {
                            k.strftime("%Y-%m-%d"): int(v)
                            for k, v in data[phrase].items()
                        },
                        "max_value": int(data[phrase].max()),
                        "avg_value": float(data[phrase].mean()),
                    }
            time.sleep(2)  # Avoid rate limiting

        except Exception as e:
            print(f"Error in batch {batch}: {str(e)}")
            continue

    return results


def analyze_and_visualize_trends(trends_data, output_dir):
    """Create visualizations and detailed analysis"""
    # Sort terms by average value
    sorted_terms = sorted(
        trends_data.items(), key=lambda x: x[1]["avg_value"], reverse=True
    )

    # 1. Create trend plot
    plt.figure(figsize=(15, 10))
    for term, data in sorted_terms[:5]:  # Top 5 terms
        dates = pd.to_datetime(list(data["trend_data"].keys()))
        values = list(data["trend_data"].values())
        plt.plot(dates, values, label=term, marker="o", markersize=3)

    plt.title("Top 5 Terms Trends (Last 3 Months)")
    plt.xlabel("Date")
    plt.ylabel("Search Interest")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_trends.png"))
    plt.close()

    # 2. Create bar chart of average values
    plt.figure(figsize=(12, 6))
    terms = [term for term, _ in sorted_terms[:10]]  # Top 10 terms
    avgs = [data["avg_value"] for _, data in sorted_terms[:10]]

    sns.barplot(x=terms, y=avgs)
    plt.title("Average Search Interest by Term (Top 10)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "average_interest.png"))
    plt.close()

    # 3. Generate detailed analysis report
    report = "Trend Analysis Report\n"
    report += "=" * 50 + "\n\n"

    for term, data in sorted_terms:
        report += f"Term: {term}\n"
        report += f"Average Interest: {data['avg_value']:.2f}\n"
        report += f"Maximum Interest: {data['max_value']}\n"
        report += (
            f"Peak Date: {max(data['trend_data'].items(), key=lambda x: x[1])[0]}\n"
        )
        report += "-" * 30 + "\n"

    with open(
        os.path.join(output_dir, "trend_analysis_report.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(report)

    return sorted_terms


def run_pipeline():
    try:
        # 1. Run scraping
        print("Running scraping task...")
        scraped_data = fetch_all_pages()
        if not scraped_data:
            raise ValueError("No data scraped")
        print(f"Scraped {len(scraped_data)} items")

        # 2. Extract and analyze trends
        # Create output directory
        output_dir = os.path.join(SCRAPING_PATH, "data", "analysis_results")
        os.makedirs(output_dir, exist_ok=True)

        print("\nAnalyzing trends...")
        titles = [item.get("judul", "") for item in scraped_data if "judul" in item]
        phrases = clean_keywords(titles)
        trends_data = get_trends_data(phrases)

        # 3. Create visualizations and analysis
        sorted_terms = analyze_and_visualize_trends(trends_data, output_dir)

        # 4. Save JSON results
        result = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_phrases": len(phrases),
                "analyzed_phrases": len(trends_data),
            },
            "trends_analysis": trends_data,
        }

        json_path = os.path.join(output_dir, "local_trends_analysis.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\nAnalysis Complete!")
        print(f"Top 5 Trending Terms:")
        for term, data in sorted_terms[:5]:
            print(f"- {term}: avg={data['avg_value']:.2f}, max={data['max_value']}")

        print(f"\nOutput files saved in: {output_dir}")
        print("- local_trends_analysis.json (complete data)")
        print("- top_trends.png (trend visualization)")
        print("- average_interest.png (average interest chart)")
        print("- trend_analysis_report.txt (detailed analysis)")

    except Exception as e:
        print(f"Pipeline failed: {str(e)}")


if __name__ == "__main__":
    run_pipeline()
