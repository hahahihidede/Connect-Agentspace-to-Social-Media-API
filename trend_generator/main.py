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
