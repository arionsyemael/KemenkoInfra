import sys
import os
import json
from datetime import datetime
from pytrends.request import TrendReq
import time

# Add Scraping path
SCRAPING_PATH = os.path.join(os.path.dirname(__file__), "Scraping")
sys.path.insert(0, SCRAPING_PATH)

# Add headers for web scraping
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

from Scraping.scraper.fetcher import fetch_all_pages


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


def run_pipeline():
    try:
        # 1. Run scraping
        print("Running scraping task...")
        scraped_data = fetch_all_pages()
        if not scraped_data:
            raise ValueError("No data scraped")
        print(f"Scraped {len(scraped_data)} items")

        # 2. Extract and analyze trends
        print("\nAnalyzing trends...")
        titles = [item.get("judul", "") for item in scraped_data if "judul" in item]
        phrases = clean_keywords(titles)
        trends_data = get_trends_data(phrases[:20])  # Limit to 20 phrases

        # 3. Save results
        print("\nSaving results...")
        result = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_phrases": len(phrases),
            },
            "trends_analysis": trends_data,
        }

        output_path = os.path.join(SCRAPING_PATH, "data", "local_trends_analysis.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\nPipeline completed successfully!")
        print(f"Results saved to: {output_path}")

    except Exception as e:
        print(f"Pipeline failed: {str(e)}")


if __name__ == "__main__":
    run_pipeline()
