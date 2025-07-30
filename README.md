# Connect-Agentspace-to-Social-Media-API

# Dokumentasi Demo Agentspace: Analisis Tren Media Sosial di Google Cloud Platform

## 1. Background
Demo ini memperlihatkan pembangunan "Agentspace" atau antarmuka AI percakapan yang cerdas. Agentspace ini dirancang untuk menganalisis dan menjawab pertanyaan tentang tren di berbagai platform media sosial, dengan data yang dikumpulkan dan disimpan secara otomatis di Google BigQuery. [cite_start]Tujuan utama demo ini adalah untuk menunjukkan bagaimana Google Cloud Platform dapat mengintegrasikan pipeline data otomatis dengan kemampuan AI generatif untuk memberikan wawasan bisnis yang real-time dan interaktif. [cite: 4, 5, 6]

## 2. Architecture

### 2.1. GCP Service Architecture
Penjelasan Alur:
* [cite_start]**Cloud Scheduler**: Memicu layanan trend-generator Cloud Run secara otomatis setiap 2 menit. [cite: 10]
* [cite_start]**Cloud Run (trend-generator)**: Menghasilkan data tren dummy yang kaya (dari platform seperti Facebook, TikTok, Twitter, Instagram) dan memasukkan data ini ke tabel daily_trends dan social_media_posts di BigQuery. [cite: 11]
* [cite_start]**BigQuery**: Berfungsi sebagai repositori data terpusat dan terstruktur untuk semua data tren yang di-ingest. [cite: 12]
* **Vertex AI Search (Data Store)**: Data dari BigQuery disinkronkan ke Data Store di Vertex AI Search. [cite_start]Ini memungkinkan agen AI untuk melakukan pencarian dan pengambilan informasi (RAG - Retrieval Augmented Generation) dari data terstruktur Anda. [cite: 13, 14]
* **Vertex AI Agent Builder**: Agen AI (SocialMediaTrendAnalyzer) yang dibangun di platform ini akan berinteraksi langsung dengan pengguna. [cite_start]Ketika pengguna mengajukan pertanyaan tentang tren, agen ini akan memanfaatkan Data Store Vertex AI Search untuk menemukan dan mengambil informasi relevan dari BigQuery, lalu menggunakan model bahasa besar (LLM) untuk menyusun jawaban yang informatif. [cite: 15, 16]

### 2.2. Data Flow Diagram
Diagram ini menunjukkan bagaimana Google Cloud Platform dapat mengotomatisasi analisis tren media sosial menggunakan agen AI percakapan. Setiap dua menit, Cloud Scheduler memicu Cloud Function untuk mengambil data terbaru dari berbagai API media sosial seperti Facebook, Instagram, TikTok, dan Twitter. Data yang dikumpulkan disimpan ke BigQuery sebagai pusat penyimpanan, lalu disinkronkan ke Vertex AI Search (Data Store). [cite_start]Agen AI bernama SocialMediaTrendAnalyzer yang dibangun di Vertex AI Agent Builder kemudian menggunakan data ini untuk menjawab pertanyaan pengguna secara cerdas dan real-time melalui Agentspace, menciptakan pengalaman analitik yang interaktif dan responsif. [cite: 18, 19, 20, 21]

## 3. GCP Service

### 3.1. BigQuery:
* **Peran**: Data Warehouse terkelola sepenuhnya untuk penyimpanan data tren media sosial yang scalable dan hemat biaya. [cite_start]Menjadi "sumber kebenaran tunggal" untuk data yang dianalisis oleh agen. [cite: 24, 25]
* [cite_start]**Detail**: Dataset social_media_trends, Tabel daily_trends (ringkasan tren) dan social_media_posts (detail postingan individu). [cite: 26]

### 3.2. Cloud Run:
* **Peran**: Layanan komputasi tanpa server yang event-driven. Digunakan sebagai generator data tren. [cite_start]Menskalakan dari nol (tanpa biaya saat idle) hingga kebutuhan. [cite: 28, 29]
* [cite_start]**Nama Layanan**: trend-generator [cite: 30]
* [cite_start]**Bahasa**: Python 3.11 [cite: 31]
* [cite_start]**Base Image**: python:3.11-slim-buster [cite: 32]

### 3.3. Cloud Scheduler:
* [cite_start]**Peran**: Penjadwal cron terkelola yang memicu layanan Cloud Run secara berkala (setiap 2 menit). [cite: 34]
* [cite_start]**Nama Job**: trigger-trend-generator [cite: 35]

### 3.4. Vertex AI Search (Discovery Engine - Data Store):
* **Peran**: Memungkinkan Anda membuat mesin pencari yang kuat dari data Anda. [cite_start]Digunakan untuk mengindeks data BigQuery dan menyediakannya untuk pengambilan informasi oleh agen AI. [cite: 37, 38]
* [cite_start]**Jenis**: Data Store Structured yang terhubung langsung ke tabel BigQuery. [cite: 39]

### 3.5. Vertex AI Agent Builder:
* **Peran**: Platform pengembangan untuk membangun agen percakapan AI yang didukung oleh model bahasa besar (LLM). [cite_start]Ini mengorkestrasi interaksi pengguna, pemanggilan tool, dan respons LLM. [cite: 41, 42]
* [cite_start]**Nama Agen**: SocialMediaTrendAnalyzer [cite: 43]
* [cite_start]**Region**: us-central1 (Region utama untuk layanan GenAI) [cite: 44]
* [cite_start]**Model**: Gemini (atau Gemini Pro) [cite: 45]

### 3.6. Cloud Function (query-bigquery-trends) - (Opsional/Alternatif Koneksi Tool):
* **Peran**: Fungsi tanpa server yang dapat berfungsi sebagai API gateway untuk mengkueri BigQuery jika Anda memilih pendekatan "Custom Tool" di Agent Builder, bukan Data Store. [cite_start]Fungsi ini di-deploy sebagai private function yang memerlukan autentikasi OIDC. [cite: 47, 48]
* [cite_start]**Nama Fungsi**: query-bigquery-trends [cite: 49]
* [cite_start]**URL**: https://asia-southeast2-YOUR_GCP_PROJECT_ID.cloudfunctions.net/query-bigquery-trends (URL ini diperlukan jika Anda memilih menggunakan Cloud Function sebagai Custom Tool). [cite: 50]

## Deployment

### A. Persiapan Lingkungan & API Media Sosial (Konseptual)
[cite_start]Sebelum mengintegrasikan data dari media sosial, Anda perlu memahami proses mendapatkan akses API yang sebenarnya. [cite: 53]
* **Pahami Kebijakan Platform**: Setiap platform (Meta/Facebook/Instagram, TikTok, X/Twitter) memiliki kebijakan API, ketentuan layanan, dan batasan penggunaan data yang berbeda. [cite_start]Penting untuk membaca dan memahami ini secara saksama. [cite: 54, 55]
* **Daftar sebagai Developer & Buat Aplikasi (App)**: Kunjungi portal developer masing-masing platform (contoh: Meta for Developers, TikTok for Developers, X Developer Platform). Buat akun developer. Daftarkan aplikasi baru (misal: "Social Media Trend Analyzer App") untuk proyek Anda. [cite_start]Aplikasi ini akan menjadi identitas Anda saat memanggil API. [cite: 56, 57, 58, 59, 60]
* **Ajukan Akses API & Lewati Proses Review**: Banyak API sosial media (terutama untuk data skala besar atau data yang berkaitan dengan pengguna) memerlukan persetujuan dan proses review yang ketat. Ini bisa melibatkan penjelasan mendetail tentang kasus penggunaan Anda. [cite_start]Dapatkan kredensial seperti API Key, API Secret, Client ID, Client Secret. [cite: 61, 62, 63, 64]
* [cite_start]**Pahami Autentikasi & Token**: Pelajari mekanisme autentikasi setiap API (umumnya OAuth 2.0) untuk mendapatkan Access Token yang diperlukan untuk memanggil endpoint API. [cite: 65]
* **Perhatikan Batasan Rate Limit**: Setiap API memiliki batasan berapa banyak permintaan yang dapat Anda lakukan dalam periode waktu tertentu (misal: per detik, per menit, per jam). [cite_start]Anda harus merancang pipeline ingest data Anda agar sesuai dengan batasan ini. [cite: 66, 67]
* [cite_start]**Gunakan SDK/Library Resmi**: Manfaatkan SDK atau library resmi yang disediakan oleh platform (jika ada) untuk memudahkan interaksi dengan API. [cite: 68]
* [cite_start]*(Catatan: Dalam demo ini, kita menggunakan data dummy yang dihasilkan oleh Cloud Run, sehingga Anda tidak perlu melalui proses persiapan API yang sebenarnya ini. Bagian ini bersifat konseptual untuk menunjukkan apa yang akan diperlukan dalam skenario dunia nyata.)* [cite: 69]

### B. Persiapan Lingkungan GCP
1.  **Pilih Project GCP**: YOUR_GCP_PROJECT_ID. [cite_start]Pastikan billing diaktifkan. [cite: 71]
2.  [cite_start]**Buka Cloud Shell**: Konsol terminal di browser. [cite: 72]
3.  [cite_start]**Konfigurasi gcloud CLI**: [cite: 73]
    ```bash
    gcloud config set project YOUR_GCP_PROJECT_ID
    gcloud components install alpha # Untuk perintah tertentu
    gcloud auth application-default login
    ```

### C. BigQuery Setup (Pusat Data Tren)
1.  [cite_start]**Aktifkan BigQuery API**: APIs & Services > Enabled APIs & Services. [cite: 78]
2.  [cite_start]**Buat BigQuery Dataset**: [cite: 79]
    * [cite_start]BigQuery Console. [cite: 80]
    * [cite_start]Dataset ID: social_media_trends [cite: 81]
    * [cite_start]Data location: asia-southeast2 (Jakarta) [cite: 82]
3.  [cite_start]**Buat Tabel BigQuery daily_trends**: [cite: 83]
    * [cite_start]Table name: daily_trends [cite: 84]
    * [cite_start]Skema (mode teks): [cite: 85]
        ```json
        [
            {"name": "keyword", "type": "STRING", "mode": "NULLABLE"},
            {"name": "date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "interest_score", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "platform", "type": "STRING", "mode": "NULLABLE"},
            {"name": "source_api", "type": "STRING", "mode": "NULLABLE"},
            {"name": "item_id", "type": "STRING", "mode": "NULLABLE"},
            {"name": "content_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "views_impressions_plays", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "likes_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "comments_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "shares_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "hashtags_list", "type": "STRING", "mode": "NULLABLE"},
            {"name": "url_link", "type": "STRING", "mode": "NULLABLE"},
            {"name": "demographic_summary", "type": "STRING", "mode": "NULLABLE"},
            {"name": "region_summary", "type": "STRING", "mode": "NULLABLE"}
        ]
        ```
    * [cite_start]Klik "CREATE TABLE". [cite: 104]
4.  [cite_start]**Buat Tabel BigQuery social_media_posts**: [cite: 105]
    * [cite_start]Table name: social_media_posts [cite: 106]
    * [cite_start]Skema (mode teks): [cite: 107]
        ```json
        [
            {"name": "post_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "trend_keyword", "type": "STRING", "mode": "NULLABLE"},
            {"name": "platform", "type": "STRING", "mode": "NULLABLE"},
            {"name": "post_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "post_type", "type": "STRING", "mode": "NULLABLE", "description": "e.g., Image, Video, Text"},
            {"name": "post_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "post_url", "type": "STRING", "mode": "NULLABLE"},
            {"name": "post_likes_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "post_comments_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "post_shares_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "post_hashtags", "type": "STRING", "mode": "NULLABLE"},
            {"name": "username", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_id", "type": "STRING", "mode": "NULLABLE"}
        ]
        ```
    * [cite_start]Klik "CREATE TABLE". [cite: 123]

### D. Cloud Run (Data Generator: trend-generator)
1.  [cite_start]**Aktifkan Cloud Run & Artifact Registry APIs**. [cite: 125]
2.  [cite_start]**Buat Direktori Kerja & File**: [cite: 126]
    ```bash
    mkdir ~/trend_generator
    cd ~/trend_generator
    ```
3.  [cite_start]**Buat Dockerfile**: [cite: 129, 130]
    ```dockerfile
    FROM python:3.11-slim-buster

    WORKDIR /app

    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

    COPY main.py .

    CMD ["functions-framework", "--target", "generate_and_store_trends", "--port", "8080"]
    ```
    [cite_start]Simpan (`Ctrl+X`, `Y`, `Enter`). [cite: 138]
4.  [cite_start]**Buat requirements.txt**: [cite: 139, 140]
    ```
    google-cloud-bigquery
    functions-framework
    ```
    [cite_start]Simpan (`Ctrl+X`, `Y`, `Enter`). [cite: 144]
5.  [cite_start]**Buat main.py**: [cite: 145, 146]
    ```python
    import os
    import datetime
    import random
    from google.cloud import bigquery
    import functions_framework
    import json

    print("DEBUG: Script started. (Global scope - trend_generator)")

    PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
    DATASET_ID = "social_media_trends"
    DAILY_TRENDS_TABLE = "daily_trends"
    POSTS_TABLE = "social_media_posts"
    print(f"DEBUG: Project/Dataset/Table IDs set. (Global scope - trend_generator)")


    @functions_framework.http
    def generate_and_store_trends(request):
        print("DEBUG: generate_and_store_trends function called.")
        try:
            client = bigquery.Client()
            print("DEBUG: BigQuery client initialized inside function.")

            rows_for_daily_trends = []
            rows_for_posts = []

            current_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
            today = datetime.date.today()

            platforms_data = {
                'Facebook': {'source': 'Meta Graph API (Ads Archive)', 'topics': ['Promo Gadget', 'Fashion Sale', 'Local Events', 'Health Tips'], 'id_prefix': 'FB_AD_', 'url_base': '[https://facebook.com/ads/](https://facebook.com/ads/)', 'post_types': ['Image', 'Video']},
                'TikTok': {'source': 'TikTok Search API', 'topics': ['Dance Challenge', 'Cooking Hacks', 'Travel Vlog', 'DIY Crafts'], 'id_prefix': 'TIK_VIDEO_', 'url_base': '[https://tiktok.com/@user/video/](https://tiktok.com/@user/video/)', 'post_types': ['Video']},
                'Twitter': {'source': 'X API (Trends/Place)', 'topics': ['Breaking News', 'Political Debate', 'Sports Update', 'Tech Insights'], 'id_prefix': 'TW_TWEET_', 'url_base': '[https://twitter.com/status/](https://twitter.com/status/)', 'post_types': ['Text', 'Image', 'Video']},
                'Instagram': {'source': 'Instagram Media API', 'topics': ['Photography Tips', 'Fitness Journey', 'Art Showcase', 'Food Photography'], 'id_prefix': 'IG_POST_', 'url_base': '[https://instagram.com/p/](https://instagram.com/p/)'}
            }

            for platform, p_data in platforms_data.items():
                for topic in p_data['topics']:
                    total_views_impressions_plays = random.randint(5_000_000, 20_000_000)
                    total_likes_count = total_views_impressions_plays // random.randint(10, 20)
                    total_comments_count = total_likes_count // random.randint(20, 50)
                    total_shares_count = total_likes_count // random.randint(10, 30)

                    keyword = f"{topic} trends on {platform}"
                    content_text_summary = f"Overall trends for {topic.lower()} on {platform} today."
                    if platform == 'Twitter':
                        keyword = f"#{topic.lower().replace(' ', '')} trending"
                    elif platform == 'TikTok':
                        keyword = f"Viral {topic.lower()} Challenge"
                    elif platform == 'Instagram':
                        keyword = f"{topic} Inspiration"
                    else: # Facebook
                        keyword = f"{topic} Discussion on Facebook"


                    demog_data = [
                        {"age": "18-24", "gender": "male", "percentage": round(random.uniform(0.1, 0.4), 2)},
                        {"age": "25-34", "gender": "female", "percentage": round(random.uniform(0.1, 0.3), 2)},
                        {"age": "35-44", "gender": "other", "percentage": round(random.uniform(0.05, 0.2), 2)}
                    ]
                    demog_summary = json.dumps(demog_data)

                    region_data = [
                        {"region": "Jakarta", "percentage": round(random.uniform(0.3, 0.6), 2)},
                        {"region": "Surabaya", "percentage": round(random.uniform(0.1, 0.3), 2)},
                        {"region": "Bandung", "percentage": round(random.uniform(0.05, 0.15), 2)}
                    ]
                    region_summary = json.dumps(region_data)

                    base_hashtags = [f"#{t.lower().replace(' ', '')}" for t in topic.split()]
                    platform_hashtags = [f"#{platform.lower()}trends", f"#{platform.lower()}{topic.replace(' ', '')}"]
                    all_hashtags = list(set(base_hashtags + platform_hashtags))
                    hashtags_list_str = " ".join(all_hashtags)

                    trend_id = f"TREND_{platform}_{topic.replace(' ', '_')}_{today.strftime('%Y%m%d')}"
                    url_link_summary = f"[https://trendsummaries.com/](https://trendsummaries.com/){trend_id}"

                    total_posts_for_trend = random.randint(50, 500)

                    rows_for_daily_trends.append({
                        "keyword": keyword,
                        "date": today.isoformat(),
                        "interest_score": total_likes_count + total_comments_count + total_shares_count,
                        "timestamp": current_timestamp,
                        "platform": platform,
                        "source_api": p_data['source'],
                        "item_id": trend_id,
                        "content_text": content_text_summary,
                        "views_impressions_plays": total_views_impressions_plays,
                        "likes_count": total_likes_count,
                        "comments_count": total_comments_count,
                        "shares_count": total_shares_count,
                        "hashtags_list": hashtags_list_str,
                        "url_link": url_link_summary,
                        "demographic_summary": demog_summary,
                        "region_summary": region_summary,
                        "total_posts_count": total_posts_for_trend
                    })

                    num_posts_to_generate = random.randint(3, 8)
                    for i in range(num_posts_to_generate):
                        post_likes = random.randint(100, 5000)
                        post_comments = post_likes // random.randint(10, 20)
                        post_shares = post_likes // random.randint(5, 10)
                        post_type = random.choice(p_data['post_types'])
                        username = f"user_{random.randint(1000,9999)}"
                        user_id = f"UID_{random.randint(10000,99999)}"

                        post_id = f"POST_{platform}_{topic.replace(' ', '_')}_{random.randint(100000, 999999)}"
                        post_url = f"{p_data['url_base']}{post_id}"
                        post_text = f"Amazing content on {topic.lower()}! #{topic.replace(' ', '')} #{platform} #{post_type.lower()}"

                        rows_for_posts.append({
                            "post_id": post_id,
                            "trend_keyword": keyword,
                            "platform": platform,
                            "post_timestamp": current_timestamp,
                            "post_type": post_type,
                            "post_text": post_text,
                            "post_url": post_url,
                            "post_likes_count": post_likes,
                            "post_comments_count": post_comments,
                            "post_shares_count": post_shares,
                            "post_hashtags": hashtags_list_str,
                            "username": username,
                            "user_id": user_id
                        })

            print(f"DEBUG: Generated total {len(rows_for_daily_trends)} trend summaries and {len(rows_for_posts)} individual posts.")

            try:
                daily_trends_table_ref = client.dataset(DATASET_ID).table(DAILY_TRENDS_TABLE)
                print(f"DEBUG: Inserting {len(rows_for_daily_trends)} rows to {DAILY_TRENDS_TABLE}")
                errors_daily_trends = client.insert_rows_json(daily_trends_table_ref, rows_for_daily_trends)
                if errors_daily_trends == []:
                    print(f"DEBUG: Successfully inserted {len(rows_for_daily_trends)} rows into {DAILY_TRENDS_TABLE}.")
                else:
                    print(f"DEBUG ERROR: Errors inserting into {DAILY_TRENDS_TABLE}: {errors_daily_trends}")

                posts_table_ref = client.dataset(DATASET_ID).table(POSTS_TABLE)
                print(f"DEBUG: Inserting {len(rows_for_posts)} rows to {POSTS_TABLE}")
                errors_posts = client.insert_rows_json(posts_table_ref, rows_for_posts)
                if errors_posts == []:
                    print(f"DEBUG: Successfully inserted {len(rows_for_posts)} rows into {POSTS_TABLE}.")
                else:
                    print(f"DEBUG ERROR: Errors inserting into {POSTS_TABLE}: {errors_posts}")

                if errors_daily_trends == [] and errors_posts == []:
                    return f"Successfully inserted {len(rows_for_daily_trends)} trends and {len(rows_for_posts)} posts.", 200
                else:
                    return f"Errors encountered during inserts. Check logs.", 500

            except Exception as e:
                print(f"DEBUG CRITICAL ERROR: An error occurred during BigQuery insert: {e}")
                return f"An error occurred during BigQuery insert: {e}", 500

        except Exception as e:
            print(f"DEBUG CRITICAL ERROR: An error occurred inside function: {e}")
            return f"An error occurred: {e}", 500
    ```
    [cite_start]Simpan (`Ctrl+X`, `Y`, `Enter`). [cite: 283]
6.  [cite_start]**Bangun & Deploy Layanan Cloud Run**: [cite: 284]
    ```bash
    docker build -t asia-southeast2-docker.pkg.dev/YOUR_GCP_PROJECT_ID/cloud-run-source-deploy/trend-generator:latest .
    docker push asia-southeast2-docker.pkg.dev/YOUR_GCP_PROJECT_ID/cloud-run-source-deploy/trend-generator:latest
    gcloud run deploy trend-generator \
    --image asia-southeast2-docker.pkg.dev/YOUR_GCP_PROJECT_ID/cloud-run-source-deploy/trend-generator:latest \
    --region asia-southeast2 \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID \
    --min-instances 1 \
    --max-instances 1 \
    --platform managed \
    --no-cpu-throttling \
    --memory 512Mi \
    --port 8080
    ```
    Pastikan untuk mengganti YOUR_GCP_PROJECT_ID dengan ID proyek GCP Anda. URL Layanan Cloud Run akan terlihat di output dari perintah gcloud run deploy ini. [cite_start]Catat URL tersebut. [cite: 298, 299, 300]

### D. Cloud Function (Endpoint Kueri BigQuery - Opsional)
(Bagian ini hanya relevan jika Anda memilih menggunakan Cloud Function sebagai Custom Tool, bukan Data Store. Anda sudah men-deploy ini sebelumnya.) [cite_start][cite: 302]
1.  [cite_start]**Aktifkan Cloud Functions API**. [cite: 303]
2.  [cite_start]**Verifikasi Konten `~/bigquery_query_function/`**: [cite: 304]
    * [cite_start]`requirements.txt`: [cite: 305]
        ```
        google-cloud-bigquery
        functions-framework
        ```
    * [cite_start]`main.py`: (Kode yang mengkueri data kaya dari BQ) [cite: 308]
        ```python
        import os
        from google.cloud import bigquery
        import functions_framework
        import json
        from typing import List, Dict, Any, Optional

        client = bigquery.Client()
        PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
        DATASET_ID = "social_media_trends"
        TABLE_ID = "daily_trends" # Fungsi ini hanya mengkueri daily_trends atau perlu disesuaikan untuk social_media_posts

        @functions_framework.http
        def query_trends(request):
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }

            if request.method == 'OPTIONS':
                return ('', 204, headers)

            try:
                request_json = request.get_json(silent=True)
                if not request_json:
                    return ("Please provide a JSON body with 'keyword'.", 400, headers)

                keyword = request_json.get("keyword")
                platform = request_json.get("platform")
                limit = request_json.get("limit", 5)

                if not keyword:
                    return ("Missing 'keyword' in request body.", 400, headers)

                # Query untuk daily_trends
                select_columns_daily = """
                keyword, date, interest_score, platform, source_api, item_id,
                content_text, views_impressions_plays, likes_count, comments_count,
                shares_count, hashtags_list, url_link, demographic_summary, region_summary, total_posts_count
                """
                where_clause_daily = f"WHERE LOWER(keyword) LIKE LOWER('%{keyword}%')"
                if platform:
                    where_clause_daily += f" AND LOWER(platform) = LOWER('{platform}')"
                query_daily = f"""
                SELECT {select_columns_daily}
                FROM `{PROJECT_ID}.{DATASET_ID}.daily_trends`
                {where_clause_daily}
                ORDER BY timestamp DESC
                LIMIT {limit}
                """

                # Query untuk social_media_posts (jika diperlukan)
                # Anda bisa menambahkan logika untuk mengkueri tabel social_media_posts
                # berdasarkan item_id dari daily_trends atau parameter lain

                query_job = client.query(query_daily) # Menjalankan query ke daily_trends
                results = [dict(row) for row in query_job.result()]

                if not results:
                    return (json.dumps({"message": f"No trends found for keyword: {keyword} on platform: {platform or 'any'}"}), 200, {'Content-Type': 'application/json', **headers})

                return (json.dumps(results), 200, {'Content-Type': 'application/json', **headers})

            except Exception as e:
                print(f"Error querying BigQuery: {e}")
                return (f"Error processing request: {e}", 500, headers)
        ```
3.  [cite_start]**Deploy Cloud Function**: [cite: 365]
    ```bash
    gcloud functions deploy query-bigquery-trends \
    --runtime python311 \
    --trigger-http \
    --entry-point query_trends \
    --set-env-vars GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID \
    --region asia-southeast2 \
    --project=YOUR_GCP_PROJECT_ID \
    --memory 256MB \
    --timeout 300s \
    --min-instances 1
    ```
    (Jika ada prompt `Allow unauthenticated invocations...?`, jawab `N`.) URL Trigger Cloud Function akan terlihat di output. [cite_start]Catat URL tersebut. [cite: 376, 377]

### E. Cloud Scheduler (Pemicu Data Generator: trigger-trend-generator)
1.  [cite_start]**Aktifkan Cloud Scheduler API**. [cite: 379]
2.  [cite_start]**Buat Cloud Scheduler Job**: [cite: 380]
    [cite_start]Catatan: Ganti YOUR_PROJECT_NUMBER dengan Project Number GCP Anda (dapat ditemukan di gcloud projects describe YOUR_GCP_PROJECT_ID --format="value(projectNumber)"). [cite: 381] [cite_start]Ganti YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL dengan email Compute Engine Default Service Account Anda (misal: [PROJECT_NUMBER]-compute@developer.gserviceaccount.com). [cite: 382] [cite_start]Ganti YOUR_CLOUD_RUN_URL dengan URL Layanan Cloud Run trend-generator Anda. [cite: 383]
    ```bash
    gcloud scheduler jobs create http trigger-trend-generator \
    --location=asia-southeast2 \
    --schedule="*/2 * * * *" \
    --uri="YOUR_CLOUD_RUN_URL" \
    --http-method=POST \
    --message-body="json={}" \
    --oidc-service-account-email="YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL" \
    --oidc-token-audience="YOUR_CLOUD_RUN_URL" \
    --headers="Content-Type=application/json" \
    --description="Trigger Cloud Run trend generator every 2 minutes"
    ```
3.  [cite_start]**Verifikasi IAM untuk Cloud Scheduler**: [cite: 394]
    [cite_start]Pastikan Compute Engine Default Service Account (YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL) memiliki peran roles/run.invoker pada layanan Cloud Run trend-generator. [cite: 395]
    ```bash
    gcloud run services add-iam-policy-binding trend-generator \
    --member=serviceAccount:YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL \
    --role=roles/run.invoker \
    --region asia-southeast2
    ```

### F. Verifikasi Aliran Data ke BigQuery
1.  **Paksa Eksekusi Cloud Scheduler**: Di konsol Cloud Scheduler, pilih job trigger-trend-generator, lalu klik "FORCE RUN". [cite_start]Verifikasi statusnya (harapannya SUCCESS atau 200 OK). [cite: 401, 402, 403]
2.  [cite_start]**Periksa Data di BigQuery (Kedua Tabel)**: [cite: 404]
    * [cite_start]daily_trends: [cite: 405]
        ```sql
        SELECT * FROM `YOUR_GCP_PROJECT_ID.social_media_trends.daily_trends` ORDER BY timestamp DESC LIMIT 20
        ```

### G. Vertex AI Search (Data Store - Koneksi Agentspace ke BigQuery)
1.  **Aktifkan Vertex AI Search API (Discovery Engine)**: Navigasikan ke APIs & Services > Enabled APIs & Services. [cite_start]Pastikan Discovery Engine API diaktifkan. [cite: 409, 410]
2.  [cite_start]**Buat Data Store**: [cite: 411]
    * [cite_start]Di konsol GCP, navigasikan ke Vertex AI > Agent Builder > Discovery Engines > Data Stores. [cite: 412]
    * [cite_start]Klik "CREATE NEW DATA STORE". [cite: 413]
    * [cite_start]Choose application type: Pilih Search for customer-facing applications. [cite: 414]
    * [cite_start]Connect data source: Pilih Data in BigQuery. [cite: 415]
    * [cite_start]Pilih dataset dan tabel BigQuery Anda: social_media_trends.daily_trends (Data Store akan mengindeks tabel ini, dan bisa juga mengindeks social_media_posts jika Anda menambahkannya sebagai sumber terpisah atau sebagai bagian dari Data Store yang sama). [cite: 416]
    * [cite_start]Ikuti langkah-langkah untuk menamai Data Store Anda. [cite: 417]

### H. Vertex AI Agent Builder (Membangun & Menguji Agentspace)
1.  **Aktifkan Agent Builder API**: Navigasikan ke APIs & Services > Enabled APIs & Services. [cite_start]Pastikan Vertex AI Agent Builder API diaktifkan. [cite: 419, 420]
2.  [cite_start]**Buat Agen "SocialMediaTrendAnalyzer"**: [cite: 421]
    * [cite_start]Di konsol GCP, navigasikan ke Vertex AI > Generative AI > AI Application. [cite: 422]
    * [cite_start]Klik "Create" (di sub-menu) atau "CREATE NEW APPLICATION". [cite: 423]
    * [cite_start]Pilih tipe aplikasi: "Chat". [cite: 424]
    * [cite_start]Application name: SocialMediaTrendAnalyzer. [cite: 425]
    * [cite_start]Region: us-central1. [cite: 426]
    * [cite_start]Model: Gemini (atau Gemini Pro). [cite: 427]
    * [cite_start]Lanjutkan proses pembuatan agen. [cite: 428]
3.  [cite_start]**Hubungkan Data Store ke Agen**: [cite: 429]
    * [cite_start]Setelah agen dibuat, di halaman konfigurasi agen Anda, cari bagian "Data stores" atau "Search". [cite: 430]
    * [cite_start]Tambahkan Data Store yang baru Anda buat (dari social_media_trends.daily_trends). [cite: 431]
4.  [cite_start]**Verifikasi IAM untuk Interaksi Agen dengan Data Store**: [cite: 432]
    * [cite_start]Temukan Service Account Agent Assist Anda (misalnya service-[PROJECT_NUMBER]@gcp-sa-dialogflow.iam.gserviceaccount.com). [cite: 433]
    * [cite_start]Untuk mendapatkan [PROJECT_NUMBER], gunakan gcloud projects describe YOUR_GCP_PROJECT_ID --format="value(projectNumber)". [cite: 434]
    * [cite_start]Berikan peran roles/discoveryengine.user kepada Service Account Agent Assist ini pada proyek Anda (YOUR_GCP_PROJECT_ID). [cite: 435]
    ```bash
    gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID \
    --member=serviceAccount:[AGENT_SERVICE_ACCOUNT_EMAIL] \
    --role=roles/discoveryengine.user
    ```
    [cite_start]Ganti [AGENT_SERVICE_ACCOUNT_EMAIL] dengan email Service Account Agent Assist Anda (ditemukan di IAM & Admin > Service Accounts). [cite: 439]
5.  [cite_start]**Uji Agen AI Anda!** [cite: 440]
    [cite_start]Di panel "Test Agent" di sisi kanan konsol Agent Builder, ajukan pertanyaan-pertanyaan yang relevan dengan data Anda (contoh: "Tren AI di TikTok?", "Berapa views untuk Dance Challenge di Instagram?"). [cite: 441]
