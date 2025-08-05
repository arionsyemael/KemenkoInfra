from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import sys
import os


# ==== Tambah path Scraping agar bisa import ====
SCRAPING_PATH = "/opt/airflow/Scraping"
sys.path.insert(0, SCRAPING_PATH)

# ==== Import modul dari folder Scraping ====
from Scraping.scraper.fetcher import fetch_all_pages
from Scraping.scraper.analyzer import word_counter
from Scraping.trends.gtrends import compare_with_trends

# ==== Default args ====
default_args = {
    "owner": "arion",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ==== DAG declaration ====
with DAG(
    dag_id="kemenko_trend_dag",
    default_args=default_args,
    start_date=datetime(2025, 7, 23),
    schedule_interval="@hourly",
    catchup=False,
    description="Monitor dan bandingkan berita KemenkoInfra dengan Google Trends",
    tags=["kemenko", "trends"],
) as dag:

    def scrape_task():
        data = fetch_all_pages()
        if not data:
            raise ValueError("Scraping menghasilkan data kosong!")
        return data

    def analyze_task(ti):
        texts = ti.xcom_pull(task_ids="scrape_task")
        if not texts:
            raise ValueError("Tidak ada teks dari scraping!")
        return word_counter(texts)

    def trends_task(ti):
        analysis_result = ti.xcom_pull(task_ids="analyze_task")
        if not analysis_result:
            raise ValueError("Analisis gagal.")
        top_keywords = [word for word, _ in analysis_result[:5]]
        return compare_with_trends(top_keywords)

    def save_output(ti):
        scraped_at = datetime.now().isoformat()
        top_words = ti.xcom_pull(task_ids="analyze_task")
        google_trends = ti.xcom_pull(task_ids="trends_task")

        result = {
            "scraped_at": scraped_at,
            "top_words": top_words,
            "google_trends": google_trends,
        }

        save_path = "/opt/airflow/Scraping/data/result_comparison.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    # ==== Tasks ====
    t1 = PythonOperator(task_id="scrape_task", python_callable=scrape_task)
    t2 = PythonOperator(task_id="analyze_task", python_callable=analyze_task)
    t3 = PythonOperator(task_id="trends_task", python_callable=trends_task)
    t4 = PythonOperator(task_id="save_output", python_callable=save_output)

    # ==== Flow ====
    t1 >> t2 >> t3 >> t4
