import json
from datetime import datetime
import re
from pytrends.request import TrendReq
import time
import nltk
from nltk.util import ngrams


def extract_phrases(text, min_length=2, max_length=4):
    """Ekstrak frasa dari teks"""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    phrases = []

    # Generate frasa dengan panjang 2-4 kata
    for n in range(min_length, max_length + 1):
        n_grams = list(ngrams(words, n))
        for gram in n_grams:
            phrase = " ".join(gram)
            phrases.append(phrase)

    return phrases


def clean_phrases_from_titles(data):
    """Ekstrak dan bersihkan frasa dari judul berita"""
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
        ]
    )

    # Frasa penting yang ingin dipertahankan
    important_phrases = {
        "kemenko infra",
        "kementerian koordinator",
        "infrastruktur dan investasi",
        "pembangunan infrastruktur",
        "koordinasi pembangunan",
        "pengembangan wilayah",
    }

    phrases = {}
    for item in data:
        if "judul" in item:
            title_phrases = extract_phrases(item["judul"])
            for phrase in title_phrases:
                # Skip jika mengandung stopwords kecuali frasa penting
                if phrase in important_phrases or not any(
                    w in stopwords for w in phrase.split()
                ):
                    phrases[phrase] = phrases.get(phrase, 0) + 1

    # Ambil frasa yang muncul lebih dari sekali dan frasa penting
    frequent_phrases = {
        p for p, count in phrases.items() if count > 1 or p in important_phrases
    }

    return list(frequent_phrases)


def compare_with_trends(phrases, timeframe="today 3-m"):
    """Ambil data trend dari Google Trends"""
    print(f"\nMengambil data trends untuk {len(phrases)} frasa...")
    pytrends = TrendReq(hl="id-ID", tz=420)
    results = {}

    for i in range(0, len(phrases), 5):
        batch = phrases[i : i + 5]
        print(f"Memproses batch {i//5 + 1}: {batch}")

        try:
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo="ID")

            interest_over_time = pytrends.interest_over_time()

            for phrase in batch:
                if phrase in interest_over_time.columns:
                    data = interest_over_time[phrase].to_dict()
                    results[phrase] = {
                        "trend_data": {
                            k.strftime("%Y-%m-%d"): int(v) for k, v in data.items()
                        },
                        "max_value": int(interest_over_time[phrase].max()),
                        "avg_value": round(interest_over_time[phrase].mean(), 2),
                    }
                    print(
                        f"✓ '{phrase}': max={results[phrase]['max_value']}, avg={results[phrase]['avg_value']}"
                    )
        except Exception as e:
            print(f"Error pada batch {batch}: {str(e)}")

        time.sleep(2)

    return results


def print_detailed_analysis(trends_data):
    """Tampilkan analisis detail untuk setiap frasa"""
    print("\n=== ANALISIS DETAIL TREND FRASA ===")

    # Urutkan frasa berdasarkan rata-rata popularitas
    sorted_phrases = sorted(
        trends_data.items(),
        key=lambda x: (x[1].get("max_value", 0), x[1].get("avg_value", 0)),
        reverse=True,
    )

    for phrase, data in sorted_phrases:
        print("\n" + "=" * 100)
        print(f"FRASA: {phrase.upper()}")
        print(f"Popularitas Maksimum: {data['max_value']}")
        print(f"Rata-rata Popularitas: {data['avg_value']:.2f}")
        print("-" * 100)

        if not data.get("trend_data"):
            print("Tidak ada data trend tersedia")
            continue

        # Kelompokkan dan tampilkan data harian
        print("\nData Harian:")
        print(f"{'Tanggal':<12} {'Nilai':<8} {'Trend':<40} {'Status':<15}")
        print("-" * 80)

        prev_value = None
        for date, value in sorted(data["trend_data"].items()):
            bar = "█" * (value // 2)

            # Tentukan status trend
            status = ""
            if prev_value is not None:
                if value > prev_value:
                    status = "↑ Naik"
                elif value < prev_value:
                    status = "↓ Turun"
                else:
                    status = "→ Tetap"
            prev_value = value

            print(f"{date:<12} {value:<8} {bar:<40} {status:<15}")

        # Statistik per periode
        periods = {"Minggu terakhir": 7, "Bulan terakhir": 30, "Total periode": None}

        print("\nStatistik per Periode:")
        print("-" * 40)

        sorted_dates = sorted(data["trend_data"].items())
        for period_name, days in periods.items():
            relevant_data = sorted_dates[-days:] if days else sorted_dates
            values = [v for _, v in relevant_data]

            if values:
                avg = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)

                print(f"\n{period_name}:")
                print(f"  Rata-rata: {avg:.2f}")
                print(f"  Maximum  : {max_val}")
                print(f"  Minimum  : {min_val}")
                print(f"  Range    : {max_val - min_val}")


def analyze_important_terms():
    """Analisis frasa dan kata penting"""
    important_terms = {
        "infrastruktur": [
            "pembangunan infrastruktur",
            "infrastruktur nasional",
            "infrastruktur berkelanjutan",
        ],
        "pembangunan": [
            "pembangunan berkelanjutan",
            "pembangunan nasional",
            "pemerataan pembangunan",
        ],
        "kolaborasi": [
            "kolaborasi strategis",
            "kolaborasi global",
            "kolaborasi pemerintah",
        ],
        "ekonomi": ["pertumbuhan ekonomi", "ekonomi berkelanjutan", "dampak ekonomi"],
        "kemenko": ["kemenko infra", "menko ahy", "kebijakan kemenko"],
    }

    def print_term_analysis(term_data):
        print(f"\n{'='*100}")
        print(f"ANALISIS TREND: {term_data['term'].upper()}")
        print(f"{'='*100}")
        print(f"Popularitas Maksimum  : {term_data['max_value']}")
        print(f"Rata-rata Popularitas : {term_data['avg_value']:.2f}")
        print(
            f"Periode Teratas       : {term_data['peak_date']} ({term_data['max_value']} poin)"
        )

        print("\nTrend Harian:")
        print(f"{'Tanggal':<12} {'Nilai':<8} {'Trend':<40} {'Status':<10}")
        print("-" * 70)

        prev_value = None
        for date, value in term_data["daily_data"]:
            bar = "█" * (value // 2)
            status = ""
            if prev_value is not None:
                if value > prev_value:
                    status = "↑"
                elif value < prev_value:
                    status = "↓"
                else:
                    status = "→"
            prev_value = value
            print(f"{date:<12} {value:<8} {bar:<40} {status:<10}")

    with open(
        "Scraping/data/detailed_trends_comparison.json", "r", encoding="utf-8"
    ) as f:
        trends_data = json.load(f)

    results = []
    for category, terms in important_terms.items():
        print(f"\n\n{'#'*120}")
        print(f"KATEGORI: {category.upper()}")
        print(f"{'#'*120}")

        for term in terms:
            if term in trends_data["trends_analysis"]:
                data = trends_data["trends_analysis"][term]
                daily_data = sorted(
                    [(date, value) for date, value in data["trend_data"].items()]
                )

                # Find peak date
                peak_date = max(daily_data, key=lambda x: x[1])[0]

                term_summary = {
                    "term": term,
                    "max_value": data["max_value"],
                    "avg_value": data["avg_value"],
                    "peak_date": peak_date,
                    "daily_data": daily_data,
                }

                print_term_analysis(term_summary)
                results.append(term_summary)

    # Sort and show overall ranking
    print("\n\nRANKING POPULARITAS KESELURUHAN")
    print("=" * 80)
    sorted_results = sorted(results, key=lambda x: x["avg_value"], reverse=True)

    for i, result in enumerate(sorted_results, 1):
        print(
            f"{i:2d}. {result['term']:<40} (Max: {result['max_value']:3d}, Avg: {result['avg_value']:6.2f})"
        )


def analyze_six_months_trends(trends_data):
    """Analisis tren 6 bulan terakhir"""
    print("\n=== ANALISIS TREND 6 BULAN TERAKHIR ===")
    print("=" * 100)

    # Sort phrases by max value
    sorted_phrases = sorted(
        trends_data.items(),
        key=lambda x: x[1]["max_value"],
        reverse=True,
    )

    for phrase, data in sorted_phrases:
        if data["max_value"] > 0:  # Only show phrases with activity
            print(f"\nFRASA: {phrase.upper()}")
            print("-" * 100)

            # Get dates and values
            trend_data = data["trend_data"]
            dates = sorted(trend_data.keys())

            # Find last active date (value > 0)
            last_active = None
            for date in reversed(dates):
                if trend_data[date] > 0:
                    last_active = date
                    break

            # Find date with maximum value
            max_date = max(trend_data.items(), key=lambda x: x[1])[0]

            print(f"Nilai Maksimum    : {data['max_value']} (pada {max_date})")
            print(f"Rata-rata         : {data['avg_value']:.2f}")
            print(f"Terakhir Diakses  : {last_active}")

            # Monthly statistics
            print("\nStatistik Bulanan:")
            monthly_stats = {}
            for date, value in trend_data.items():
                month = date[:7]  # YYYY-MM
                if month not in monthly_stats:
                    monthly_stats[month] = []
                monthly_stats[month].append(value)

            for month in sorted(monthly_stats.keys(), reverse=True)[
                :6
            ]:  # Last 6 months
                values = monthly_stats[month]
                avg = sum(values) / len(values)
                max_val = max(values)
                active_days = sum(1 for v in values if v > 0)

                print(f"\n{month}:")
                print(f"  Rata-rata    : {avg:.2f}")
                print(f"  Maximum      : {max_val}")
                print(f"  Hari Aktif   : {active_days} dari {len(values)} hari")

                # Visual representation
                print("  Trend        : ", end="")
                for value in values:
                    if value >= 75:
                        print("🔴", end="")  # High activity
                    elif value >= 50:
                        print("🟡", end="")  # Medium activity
                    elif value >= 25:
                        print("🟢", end="")  # Low activity
                    elif value > 0:
                        print("⚪", end="")  # Very low activity
                    else:
                        print("·", end="")  # No activity
                print()


def analyze_content_trends(content_data):
    """Analyze both phrases and individual words"""
    
    # Extract individual words from phrases
    words = {}
    for phrase in content_data['phrases']:
        for word in phrase.split():
            if len(word) > 3:  # Only words longer than 3 chars
                if word not in words:
                    words[word] = {'count': 0, 'phrases': set()}
                words[word]['count'] += 1
                words[word]['phrases'].add(phrase)

    # Combine phrases and words analysis
    combined_analysis = {
        'phrases': content_data['trends_analysis'],
        'words': words
    }

    return combined_analysis

def print_sorted_trends(analysis_data):
    """Print sorted trends by popularity"""
    print("\n=== ANALISIS TREND TERURUT BERDASARKAN POPULARITAS ===")
    print("=" * 100)

    # Combine and sort all trends
    all_trends = []
    
    # Add phrases with their metrics
    for phrase, data in analysis_data['phrases'].items():
        if data['max_value'] > 0:  # Only include items with activity
            all_trends.append({
                'type': 'Frasa',
                'content': phrase,
                'max_value': data['max_value'],
                'avg_value': data['avg_value'],
                'trend_data': data['trend_data']
            })
    
    # Sort by max_value and avg_value
    sorted_trends = sorted(
        all_trends,
        key=lambda x: (x['max_value'], x['avg_value']),
        reverse=True
    )

    # Print results
    print(f"\n{'TIPE':<8} {'KONTEN':<40} {'MAX':<6} {'AVG':<6} {'TERAKHIR AKTIF':<12}")
    print("-" * 80)

    for trend in sorted_trends:
        # Find last active date
        last_active = "Tidak ada"
        for date, value in sorted(trend['trend_data'].items(), reverse=True):
            if value > 0:
                last_active = date
                break

        print(f"{trend['type']:<8} {trend['content']:<40} {trend['max_value']:<6} "
              f"{trend['avg_value']:<6.2f} {last_active}")

    # Print most used words
    print("\n=== KATA-KATA YANG SERING MUNCUL ===")
    print("-" * 80)
    sorted_words = sorted(analysis_data['words'].items(), 
                         key=lambda x: x[1]['count'], 
                         reverse=True)[:20]
    
    for word, data in sorted_words:
        print(f"\nKata: {word} (muncul {data['count']} kali)")
        print("Dalam frasa:")
        for phrase in sorted(data['phrases'])[:5]:  # Show up to 5 phrases
            print(f"- {phrase}")

def create_enhanced_analysis(news_data, trends_data):
    """Create enhanced analysis structure for JSON output"""
    
    # Analyze words frequency
    word_frequency = {}
    for item in news_data:
        if 'judul' in item:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', item['judul'].lower())
            for word in words:
                if word not in word_frequency:
                    word_frequency[word] = {
                        'count': 0,
                        'contexts': []
                    }
                word_frequency[word]['count'] += 1
                if len(word_frequency[word]['contexts']) < 5:  # Keep up to 5 examples
                    word_frequency[word]['contexts'].append(item['judul'])

    # Sort trends by popularity
    sorted_trends = []
    for phrase, data in trends_data.items():
        if data['max_value'] > 0:
            peak_date = max(data['trend_data'].items(), key=lambda x: x[1])[0]
            last_active = max((d for d, v in data['trend_data'].items() if v > 0), default=None)
            
            monthly_stats = {}
            for date, value in data['trend_data'].items():
                month = date[:7]
                if month not in monthly_stats:
                    monthly_stats[month] = {
                        'values': [],
                        'active_days': 0
                    }
                monthly_stats[month]['values'].append(value)
                if value > 0:
                    monthly_stats[month]['active_days'] += 1

            sorted_trends.append({
                'phrase': phrase,
                'statistics': {
                    'max_value': data['max_value'],
                    'avg_value': data['avg_value'],
                    'peak_date': peak_date,
                    'last_active': last_active
                },
                'monthly_analysis': {
                    month: {
                        'avg': sum(stats['values']) / len(stats['values']),
                        'max': max(stats['values']),
                        'active_days': stats['active_days'],
                        'total_days': len(stats['values'])
                    }
                    for month, stats in monthly_stats.items()
                },
                'daily_data': data['trend_data']
            })
    
    # Sort by max_value and then avg_value
    sorted_trends.sort(key=lambda x: (
        x['statistics']['max_value'], 
        x['statistics']['avg_value']
    ), reverse=True)

    # Create final structure
    return {
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "total_trends_analyzed": len(trends_data),
            "total_words_analyzed": len(word_frequency)
        },
        "trend_analysis": {
            "sorted_trends": sorted_trends,
            "word_frequency": {
                word: data for word, data in sorted(
                    word_frequency.items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )[:50]  # Top 50 words
            }
        }
    }

def clean_keywords(titles):
    """Extract meaningful keywords from titles"""
    # Define important terms explicitly
    important_terms = [
        "kemenko infra",
        "kementerian koordinator",
        "infrastruktur dan investasi", 
        "pembangunan infrastruktur",
        "koordinasi pembangunan",
        "pengembangan wilayah",
        "ahy",
        "ici",
        "seawall",
        "sea wall"
    ]

    # Add variations and combinations
    variations = [
        "infrastruktur nasional",
        "menko ahy",
        "pembangunan berkelanjutan",
        "koordinasi infrastruktur",
        "pengembangan infrastruktur"
    ]

    all_terms = set(important_terms + variations)
    
    # Extract matching terms from titles
    matches = {}
    for term in all_terms:
        count = sum(1 for title in titles if term.lower() in title.lower())
        if count > 0:
            matches[term] = count
    
    # Sort by frequency
    sorted_terms = sorted(matches.items(), key=lambda x: x[1], reverse=True)
    return [term for term, _ in sorted_terms]

def main():
    # 1. Jalankan scraper untuk data terbaru
    try:
        import subprocess

        print("Mengupdate data dari website...")
        subprocess.run(["python", "Scraping/main.py"], check=True)
    except Exception as e:
        print(f"Warning: Gagal update data: {str(e)}")

    # 2. Baca data berita
    try:
        with open("Scraping/data/berita.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
        print(f"Berhasil membaca {len(news_data)} berita")
    except FileNotFoundError:
        print("Error: File berita.json tidak ditemukan!")
        return

    # 3. Ekstrak frasa
    phrases = clean_phrases_from_titles(news_data)
    print(f"\nDitemukan {len(phrases)} frasa unik")

    # 4. Ambil data trends (10 frasa teratas)
    trends_data = compare_with_trends(phrases[:10])

    # 5. Tampilkan analisis detail
    print_detailed_analysis(trends_data)

    # 6. Simpan hasil lengkap
    result = {
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "total_phrases": len(phrases),
            "analyzed_phrases": len(trends_data),
        },
        "phrases": phrases,
        "trends_analysis": trends_data,
    }

    output_path = "Scraping/data/detailed_trends_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nHasil lengkap telah disimpan ke {output_path}")

    # Create and save enhanced analysis
    enhanced_analysis = create_enhanced_analysis(news_data, trends_data)
    enhanced_output_path = "Scraping/data/enhanced_analysis.json"
    with open(enhanced_output_path, "w", encoding="utf-8") as f:
        json.dump(enhanced_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Analisis lengkap telah disimpan ke {enhanced_output_path}")


if __name__ == "__main__":
    try:
        main()
        analyze_important_terms()
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh user")
    except Exception as e:
        print(f"\nError: {str(e)}")
