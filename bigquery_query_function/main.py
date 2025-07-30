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
