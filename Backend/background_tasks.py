import json
import os
from datetime import datetime, timedelta
from google_trends import daily_trends, realtime_trends
from flask import Flask

app = Flask(__name__)


# docs, orig = load_data("csvProcessing/allData.json")
# model = ensemble(docs,use_translation=True, origdocs=orig, use_date_level= 0 or 1)
# OR
# model = ensemble(docs,use_translation=True, origdocs=orig)
# OR
# set model.use_date_level = 1 before calling the api, and set it to 2 again once done


def fetch_and_store_top_trends():
    try:
        print("Fetching and storing top trends...")
        # Fetch daily trends for today and yesterday
        today_trends = daily_trends(country="IN")
        yesterday = datetime.today() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y%m%d")
        yesterday_trends = daily_trends(date=yesterday_str, country="IN")

        # Combine today's and yesterday's trends and take the union
        combined_trends = set(today_trends + yesterday_trends)
        print(combined_trends)
        combined_results = []
        for query in combined_trends:
            # Call the rank_documents_bm25_bert function for each query
            req = {"query": query}
            with app.test_request_context(json=req):
                from app import (
                    rank_documents_bm25_bert,
                    rank_documents_bm25_bert_trends,
                )  # Import here to avoid circular import

                response = rank_documents_bm25_bert_trends()
                if response.status_code == 200:
                    result_data = response.json
                    if result_data:
                        top_story_percentage = (
                            result_data[0]["percentage"] if result_data else 0
                        )
                        combined_results.append(
                            {
                                "query": query,
                                "top_story_percentage": top_story_percentage,
                                "result_data": result_data,
                            }
                        )

        # Sort combined results based on top story percentage
        sorted_results = sorted(
            combined_results, key=lambda x: x["top_story_percentage"], reverse=True
        )

        # Get the top 5 queries with the highest match percentages
        top_5_results = sorted_results[:5]

        # Prepare the response in the required format
        response_data = [
            {result["query"]: result["result_data"][:1]} for result in top_5_results
        ]

        # Store the response data in a file
        with open("top_trends_cache.json", "w", encoding="utf-8") as cache_file:
            json.dump(response_data, cache_file, ensure_ascii=False, indent=4)
        print("Top trends stored successfully!")
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")
