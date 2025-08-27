from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import sys
import os
import re
from pytrends.request import TrendReq
import time
from airflow.utils.log.logging_mixin import LoggingMixin

# Add Scraping path
SCRAPING_PATH = os.path.join(os.getenv("AIRFLOW_HOME", ""), "Scraping")
sys.path.insert(0, SCRAPING_PATH)

from Scraping.scraper.fetcher import fetch_all_pages

default_args = {
    "owner": "arion",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
    "depends_on_past": False,
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
            "sebagai",
            "juga",
            "akan",
            "sudah",
            "telah",
            "bisa",
            "dapat",
            "saat",
            "ketika",
            "dimana",
        ]
    )

    important_phrases = {
        "kemenko infra",
        "menko infrastruktur",
        "pembangunan infrastruktur",
        "infrastruktur nasional",
        "koordinasi pembangunan",
        "ahy",
        "sea wall",
        "seawall",
        "tanggul laut",
        "kemenko infrastruktur",
        "pembangunan berkelanjutan",
        "investasi infrastruktur",
        "pengembangan wilayah",
        "koordinasi pembangunan",
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


def scrape_task(**context):
    logger = LoggingMixin().log
    logger.info("Starting scraping task...")
    try:
        data = fetch_all_pages()
        if not data:
            raise ValueError("No data scraped")  # Add proper error handling
        logger.info(f"Scraping completed. Got {len(data)} items")
        return data
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


def analyze_trends_task(**context):
    """Analyze trends data"""
    try:
        ti = context["ti"]
        scraped_data = ti.xcom_pull(task_ids="scrape_news")

        # Extract titles
        titles = [item.get("judul", "") for item in scraped_data if "judul" in item]

        # Get keywords and trends
        phrases = clean_keywords(titles)
        trends_data = get_trends_data(phrases[:20])  # Limit to 20 phrases

        result = {
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "total_phrases": len(phrases),
            },
            "trend_analysis": trends_data,
        }

        return result

    except Exception as e:
        raise Exception(f"Trends analysis failed: {str(e)}")


def save_results_task(**context):
    """Save analysis results"""
    try:
        ti = context["ti"]
        result = ti.xcom_pull(task_ids="analyze_trends")

        if not result:
            raise ValueError("No analysis results to save")

        output_path = os.path.join(
            SCRAPING_PATH, "data", "airflow_trends_analysis.json"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    except Exception as e:
        raise Exception(f"Saving results failed: {str(e)}")


def check_paths():
    required_paths = [
        SCRAPING_PATH,
        os.path.join(SCRAPING_PATH, "data"),
        os.path.join(SCRAPING_PATH, "scraper"),
    ]
    for path in required_paths:
        if not os.path.exists(path):
            raise Exception(f"Required path not found: {path}")


def validate_environment():
    logger = LoggingMixin().log
    logger.info(f"Checking environment setup...")
    logger.info(f"AIRFLOW_HOME: {os.getenv('AIRFLOW_HOME')}")
    logger.info(f"SCRAPING_PATH: {SCRAPING_PATH}")

    if not os.path.exists(SCRAPING_PATH):
        raise Exception(f"Scraping path not found: {SCRAPING_PATH}")


with DAG(
    dag_id="kemenko_trends_monitoring",
    default_args=default_args,
    description="Monitor news trends from Kemenko website",
    schedule_interval="@daily",
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["kemenko", "monitoring"],
) as dag:

    validate_env = PythonOperator(
        task_id="validate_environment", python_callable=validate_environment, dag=dag
    )

    scrape_news = PythonOperator(
        task_id="scrape_news",
        python_callable=scrape_task,
        retries=3,
        retry_delay=timedelta(minutes=5),
        provide_context=True,
        dag=dag,
    )

    analyze_trends = PythonOperator(
        task_id="analyze_trends",
        python_callable=analyze_trends_task,
        provide_context=True,
    )

    save_results = PythonOperator(
        task_id="save_results",
        python_callable=save_results_task,
        provide_context=True,
    )

    # Set task dependencies
    validate_env >> scrape_news >> analyze_trends >> save_results
