# Demo Agentspace: Analisis Tren Media Sosial dengan Google Cloud Platform

Proyek ini mendemonstrasikan pembangunan sebuah "Agentspace" — antarmuka AI percakapan cerdas — yang dirancang untuk menganalisis dan menjawab pertanyaan tentang tren di berbagai platform media sosial. Data tren secara otomatis dikumpulkan dan disimpan di Google BigQuery. Tujuan utamanya adalah untuk menunjukkan bagaimana Google Cloud Platform (GCP) dapat mengintegrasikan pipeline data otomatis dengan kemampuan AI generatif untuk memberikan wawasan bisnis yang real-time dan interaktif.

## 🚀 Arsitektur

### Diagram Alur Layanan GCP

Arsitektur ini melibatkan beberapa layanan GCP yang bekerja bersama:

1.  **Cloud Scheduler**: Memicu layanan `trend-generator` (Cloud Run) secara otomatis setiap 2 menit.
2.  **Cloud Run (trend-generator)**: Menghasilkan data tren dummy dari platform seperti Facebook, TikTok, Twitter, dan Instagram, lalu memasukkan data ini ke tabel `daily_trends` dan `social_media_posts` di BigQuery.
3.  **BigQuery**: Berfungsi sebagai repositori data terpusat dan terstruktur untuk semua data tren yang di-ingest.
4.  **Vertex AI Search (Data Store)**: Data dari BigQuery disinkronkan ke Data Store di Vertex AI Search. Ini memungkinkan agen AI untuk melakukan *Retrieval Augmented Generation* (RAG) dari data terstruktur.
5.  **Vertex AI Agent Builder**: Agen AI (`SocialMediaTrendAnalyzer`) yang dibangun di platform ini akan berinteraksi langsung dengan pengguna. Agen ini memanfaatkan Data Store Vertex AI Search untuk menemukan dan mengambil informasi relevan dari BigQuery, lalu menggunakan Model Bahasa Besar (LLM) untuk menyusun jawaban yang informatif.

### Data Flow Diagram

Diagram ini mengilustrasikan otomatisasi analisis tren media sosial menggunakan agen AI percakapan. Setiap dua menit, Cloud Scheduler memicu Cloud Run untuk menghasilkan dan menyimpan data dummy ke BigQuery. Data ini kemudian disinkronkan ke Vertex AI Search (Data Store). Agen AI `SocialMediaTrendAnalyzer` di Vertex AI Agent Builder menggunakan data ini untuk menjawab pertanyaan pengguna secara cerdas dan real-time melalui Agentspace, menyediakan pengalaman analitik yang interaktif dan responsif.

## 🛠️ Layanan GCP yang Digunakan

* **BigQuery**
    * **Peran**: Data Warehouse terkelola sepenuhnya untuk penyimpanan data tren media sosial yang scalable dan hemat biaya. Bertindak sebagai "single source of truth".
    * **Detail**: Dataset `social_media_trends` dengan tabel `daily_trends` (ringkasan tren) dan `social_media_posts` (detail postingan individu).

* **Cloud Run**
    * **Peran**: Layanan komputasi tanpa server yang event-driven, digunakan sebagai generator data tren. Menskalakan dari nol hingga memenuhi permintaan.
    * **Nama Layanan**: `trend-generator`
    * **Bahasa**: Python 3.11
    * **Base Image**: `python:3.11-slim-buster`

* **Cloud Scheduler**
    * **Peran**: Penjadwal cron terkelola yang memicu layanan Cloud Run secara berkala (setiap 2 menit).
    * **Nama Job**: `trigger-trend-generator`

* **Vertex AI Search (Discovery Engine - Data Store)**
    * **Peran**: Memungkinkan pembuatan mesin pencari yang kuat dari data Anda. Mengindeks data BigQuery dan membuatnya tersedia untuk pengambilan informasi oleh agen AI.
    * **Jenis**: Data Store Structured yang terhubung langsung ke tabel BigQuery.

* **Vertex AI Agent Builder**
    * **Peran**: Platform pengembangan untuk membangun agen AI percakapan yang didukung oleh LLM. Mengorkestrasi interaksi pengguna, pemanggilan tool, dan respons LLM.
    * **Nama Agen**: `SocialMediaTrendAnalyzer`
    * **Region**: `us-central1` (Region utama untuk layanan Generative AI).
    * **Model**: Gemini (atau Gemini Pro).

* **(Opsional/Alternatif) Cloud Function (`query-bigquery-trends`)**
    * **Peran**: Fungsi tanpa server yang dapat berfungsi sebagai API gateway untuk mengkueri BigQuery jika pendekatan "Custom Tool" dipilih di Agent Builder.
    * **Nama Fungsi**: `query-bigquery-trends`
    * **URL (contoh)**: `https://asia-southeast2-YOUR_GCP_PROJECT_ID.cloudfunctions.net/query-bigquery-trends`

## 🚀 Langkah-langkah Deployment

### A. Persiapan Lingkungan & API Media Sosial (Konseptual)
*(Catatan: Dalam demo ini, kita menggunakan data dummy yang dihasilkan oleh Cloud Run, sehingga Anda tidak perlu melalui proses persiapan API yang sebenarnya ini. Bagian ini bersifat konseptual untuk menunjukkan apa yang akan diperlukan dalam skenario dunia nyata.)*

* **Pahami Kebijakan Platform**: Setiap platform (Meta/Facebook/Instagram, TikTok, X/Twitter) memiliki kebijakan API, ketentuan layanan, dan batasan penggunaan data yang berbeda.
* **Daftar sebagai Developer & Buat Aplikasi**: Kunjungi portal developer masing-masing platform.
* **Ajukan Akses API & Lewati Proses Review**: Banyak API sosial media memerlukan persetujuan dan proses review yang ketat.
* **Pahami Autentikasi & Token**: Pelajari mekanisme autentikasi setiap API (umumnya OAuth 2.0).
* **Perhatikan Batasan Rate Limit**: Rancang pipeline data Anda agar sesuai dengan batasan ini.
* **Gunakan SDK/Library Resmi**: Manfaatkan SDK atau library resmi untuk memudahkan interaksi API.

### B. Persiapan Lingkungan GCP

1.  **Pilih Project GCP Anda**: Ganti `YOUR_GCP_PROJECT_ID` dengan ID proyek Anda. Pastikan billing diaktifkan.
2.  **Buka Cloud Shell**.
3.  **Konfigurasi `gcloud` CLI**:
    ```bash
    gcloud config set project YOUR_GCP_PROJECT_ID
    gcloud components install alpha # Untuk perintah tertentu
    gcloud auth application-default login
    ```

### C. BigQuery Setup (Pusat Data Tren)

1.  **Aktifkan BigQuery API**.
2.  **Buat BigQuery Dataset**:
    * Di konsol BigQuery, buat dataset dengan ID: `social_media_trends`.
    * Lokasi data: `asia-southeast2` (Jakarta).
3.  **Buat Tabel BigQuery `daily_trends`**:
    * Nama tabel: `daily_trends`.
    * Skema (mode teks):
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
            {"name": "region_summary", "type": "STRING", "mode": "NULLABLE"},
            {"name": "total_posts_count", "type": "INTEGER", "mode": "NULLABLE"}
        ]
        ```
    * Klik "CREATE TABLE".
4.  **Buat Tabel BigQuery `social_media_posts`**:
    * Nama tabel: `social_media_posts`.
    * Skema (mode teks):
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
    * Klik "CREATE TABLE".

### D. Cloud Run (Data Generator: `trend-generator`)

1.  **Aktifkan Cloud Run & Artifact Registry APIs**.
2.  **Buat Direktori Kerja & File**:
    ```bash
    mkdir ~/trend_generator
    cd ~/trend_generator
    ```
3.  **Buat `Dockerfile`**:
    ```dockerfile
    FROM python:3.11-slim-buster

    WORKDIR /app

    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

    COPY main.py .

    CMD ["functions-framework", "--target", "generate_and_store_trends", "--port", "8080"]
    ```
4.  **Buat `requirements.txt`**:
    ```
    google-cloud-bigquery
    functions-framework
    ```
5.  **Buat `main.py`**:
    ```python
    import os
    import datetime
    import random
    from google.cloud import bigquery
    import functions_framework
    import json

    # Print debug statements to trace execution flow
    print("DEBUG: Script started. (Global scope - trend_generator)")

    # Environment variables or default values
    PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_GCP_PROJECT_ID")
    DATASET_ID = "social_media_trends"
    DAILY_TRENDS_TABLE = "daily_trends"
    POSTS_TABLE = "social_media_posts"
    print(f"DEBUG: Project/Dataset/Table IDs set. (Global scope - trend_generator)")

    @functions_framework.http
    def generate_and_store_trends(request):
        print("DEBUG: generate_and_store_trends function called.")
        try:
            # Initialize BigQuery client inside the function to ensure fresh connection per invocation
            client = bigquery.Client()
            print("DEBUG: BigQuery client initialized inside function.")

            rows_for_daily_trends = []
            rows_for_posts = []

            current_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
            today = datetime.date.today()

            # Define platforms and their associated data for dummy generation
            platforms_data = {
                'Facebook': {'source': 'Meta Graph API (Ads Archive)', 'topics': ['Promo Gadget', 'Fashion Sale', 'Local Events', 'Health Tips'], 'id_prefix': 'FB_AD_', 'url_base': '[https://facebook.com/ads/](https://facebook.com/ads/)', 'post_types': ['Image', 'Video']},
                'TikTok': {'source': 'TikTok Search API', 'topics': ['Dance Challenge', 'Cooking Hacks', 'Travel Vlog', 'DIY Crafts'], 'id_prefix': 'TIK_VIDEO_', 'url_base': '[https://tiktok.com/@user/video/](https://tiktok.com/@user/video/)', 'post_types': ['Video']},
                'Twitter': {'source': 'X API (Trends/Place)', 'topics': ['Breaking News', 'Political Debate', 'Sports Update', 'Tech Insights'], 'id_prefix': 'TW_TWEET_', 'url_base': '[https://twitter.com/status/](https://twitter.com/status/)', 'post_types': ['Text', 'Image', 'Video']},
                'Instagram': {'source': 'Instagram Media API', 'topics': ['Photography Tips', 'Fitness Journey', 'Art Showcase', 'Food Photography'], 'id_prefix': 'IG_POST_', 'url_base': '[https://instagram.com/p/](https://instagram.com/p/)', 'post_types': ['Image', 'Video']}
            }

            # Loop through platforms and topics to generate data
            for platform, p_data in platforms_data.items():
                for topic in p_data['topics']:
                    # Generate realistic-ish dummy metrics for daily trends
                    total_views_impressions_plays = random.randint(5_000_000, 20_000_000)
                    total_likes_count = total_views_impressions_plays // random.randint(10, 20)
                    total_comments_count = total_likes_count // random.randint(20, 50)
                    total_shares_count = total_likes_count // random.randint(10, 30)

                    # Generate keyword and content summary
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

                    # Dummy demographic and region summaries (as JSON strings)
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

                    # Generate hashtags
                    base_hashtags = [f"#{t.lower().replace(' ', '')}" for t in topic.split()]
                    platform_hashtags = [f"#{platform.lower()}trends", f"#{platform.lower()}{topic.replace(' ', '')}"]
                    all_hashtags = list(set(base_hashtags + platform_hashtags))
                    hashtags_list_str = " ".join(all_hashtags)

                    # Generate unique IDs and URLs
                    trend_id = f"TREND_{platform}_{topic.replace(' ', '_')}_{today.strftime('%Y%m%d')}"
                    url_link_summary = f"[https://trendsummaries.com/](https://trendsummaries.com/){trend_id}"

                    total_posts_for_trend = random.randint(50, 500) # Dummy count of posts contributing to the trend

                    # Append data to daily_trends list
                    rows_for_daily_trends.append({
                        "keyword": keyword,
                        "date": today.isoformat(),
                        "interest_score": total_likes_count + total_comments_count + total_shares_count, # Simple score
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

                    # Generate a few dummy social media posts for each trend
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

                        # Append data to social_media_posts list
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

            # Insert generated data into BigQuery tables
            try:
                # Insert into daily_trends table
                daily_trends_table_ref = client.dataset(DATASET_ID).table(DAILY_TRENDS_TABLE)
                print(f"DEBUG: Inserting {len(rows_for_daily_trends)} rows to {DAILY_TRENDS_TABLE}")
                errors_daily_trends = client.insert_rows_json(daily_trends_table_ref, rows_for_daily_trends)
                if errors_daily_trends == []:
                    print(f"DEBUG: Successfully inserted {len(rows_for_daily_trends)} rows into {DAILY_TRENDS_TABLE}.")
                else:
                    print(f"DEBUG ERROR: Errors inserting into {DAILY_TRENDS_TABLE}: {errors_daily_trends}")

                # Insert into social_media_posts table
                posts_table_ref = client.dataset(DATASET_ID).table(POSTS_TABLE)
                print(f"DEBUG: Inserting {len(rows_for_posts)} rows to {POSTS_TABLE}")
                errors_posts = client.insert_rows_json(posts_table_ref, rows_for_posts)
                if errors_posts == []:
                    print(f"DEBUG: Successfully inserted {len(rows_for_posts)} rows into {POSTS_TABLE}.")
                else:
                    print(f"DEBUG ERROR: Errors inserting into {POSTS_TABLE}: {errors_posts}")

                # Return success or error message
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
6.  **Bangun & Deploy Layanan Cloud Run**:
    Ganti `YOUR_GCP_PROJECT_ID` dengan ID proyek GCP Anda. URL Layanan Cloud Run akan terlihat di output. Catat URL tersebut.
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

### E. Cloud Function (Endpoint Kueri BigQuery - Opsional)

*(Bagian ini hanya relevan jika Anda memilih menggunakan Cloud Function sebagai Custom Tool, bukan Data Store.)*

1.  **Aktifkan Cloud Functions API**.
2.  **Verifikasi Konten Direktori Fungsi (`~/bigquery_query_function/`)**:
    * `requirements.txt`:
        ```
        google-cloud-bigquery
        functions-framework
        ```
    * `main.py`:
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
3.  **Deploy Cloud Function**:
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
    Jika diminta "Allow unauthenticated invocations...?", jawab `N`. Catat URL Trigger Cloud Function.

### F. Cloud Scheduler (Pemicu Data Generator: `trigger-trend-generator`)

1.  **Aktifkan Cloud Scheduler API**.
2.  **Buat Cloud Scheduler Job**:
    Ganti `YOUR_PROJECT_NUMBER` dengan Project Number GCP Anda (gunakan `gcloud projects describe YOUR_GCP_PROJECT_ID --format="value(projectNumber)"`). Ganti `YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL` dengan email Compute Engine Default Service Account Anda (misal: `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`). Ganti `YOUR_CLOUD_RUN_URL` dengan URL Layanan Cloud Run `trend-generator` Anda.
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
3.  **Verifikasi IAM untuk Cloud Scheduler**:
    Pastikan Compute Engine Default Service Account (`YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL`) memiliki peran `roles/run.invoker` pada layanan Cloud Run `trend-generator`.
    ```bash
    gcloud run services add-iam-policy-binding trend-generator \
    --member=serviceAccount:YOUR_COMPUTE_SERVICE_ACCOUNT_EMAIL \
    --role=roles/run.invoker \
    --region asia-southeast2
    ```

### G. Verifikasi Aliran Data ke BigQuery

1.  **Paksa Eksekusi Cloud Scheduler**: Di konsol Cloud Scheduler, pilih job `trigger-trend-generator`, lalu klik "FORCE RUN". Verifikasi statusnya (harapannya SUCCESS atau 200 OK).
2.  **Periksa Data di BigQuery (Kedua Tabel)**:
    * `daily_trends`:
        ```sql
        SELECT * FROM `YOUR_GCP_PROJECT_ID.social_media_trends.daily_trends` ORDER BY timestamp DESC LIMIT 20
        ```

### H. Vertex AI Search (Data Store - Koneksi Agentspace ke BigQuery)

1.  **Aktifkan Vertex AI Search API (Discovery Engine)**.
2.  **Buat Data Store**:
    * Di konsol GCP, navigasikan ke **Vertex AI > Agent Builder > Discovery Engines > Data Stores**.
    * Klik "CREATE NEW DATA STORE".
    * Pilih tipe aplikasi: `Search for customer-facing applications`.
    * Hubungkan sumber data: `Data in BigQuery`.
    * Pilih dataset dan tabel BigQuery Anda: `social_media_trends.daily_trends`.
    * Ikuti langkah-langkah untuk menamai Data Store Anda.

### I. Vertex AI Agent Builder (Membangun & Menguji Agentspace)

1.  **Aktifkan Agent Builder API**.
2.  **Buat Agen "SocialMediaTrendAnalyzer"**:
    * Di konsol GCP, navigasikan ke **Vertex AI > Generative AI > AI Application**.
    * Klik "Create" (atau "CREATE NEW APPLICATION").
    * Pilih tipe aplikasi: `Chat`.
    * Nama aplikasi: `SocialMediaTrendAnalyzer`.
    * Region: `us-central1`.
    * Model: `Gemini` (atau `Gemini Pro`).
    * Lanjutkan proses pembuatan agen.
3.  **Hubungkan Data Store ke Agen**:
    * Di halaman konfigurasi agen, temukan bagian "Data stores" atau "Search".
    * Tambahkan Data Store yang baru Anda buat (dari `social_media_trends.daily_trends`).
4.  **Verifikasi IAM untuk Interaksi Agen dengan Data Store**:
    * Temukan Service Account Agent Assist Anda (misalnya `service-[PROJECT_NUMBER]@gcp-sa-dialogflow.iam.gserviceaccount.com`). Gunakan `gcloud projects describe YOUR_GCP_PROJECT_ID --format="value(projectNumber)"` untuk mendapatkan `[PROJECT_NUMBER]`.
    * Berikan peran `roles/discoveryengine.user` kepada Service Account Agent Assist ini pada proyek Anda (`YOUR_GCP_PROJECT_ID`).
    ```bash
    gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID \
    --member=serviceAccount:[AGENT_SERVICE_ACCOUNT_EMAIL] \
    --role=roles/discoveryengine.user
    ```
    Ganti `[AGENT_SERVICE_ACCOUNT_EMAIL]` dengan email Service Account Agent Assist Anda.
5.  **Uji Agen AI Anda!**
    Di panel "Test Agent" di sisi kanan konsol Agent Builder, ajukan pertanyaan-pertanyaan yang relevan dengan data Anda (contoh: "Tren AI di TikTok?", "Berapa views untuk Dance Challenge di Instagram?").
