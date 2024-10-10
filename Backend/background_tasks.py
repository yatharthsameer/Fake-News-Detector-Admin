import json
import os
from datetime import datetime, timedelta
from google_trends import daily_trends, realtime_trends
import spacy


NUM_TRENDS = 6


TEST_LOCAL = __name__ == "__main__"

if not TEST_LOCAL:
    from flask import Flask

    app = Flask(__name__)

else:
    from BERTClasses import load_data, ensemble

    docs, origdata = load_data("csvProcessing/allData.json")
    model = ensemble(docs, use_translation=True, orig_docs=origdata, use_date_level=1)


#############################################################
#############################################################

NLP = spacy.load("en_core_web_sm")


def extract_entity_groups(queries):
    groups = [[] for i in range(6)]

    allqueryset = set()

    for text in queries:
        doc = NLP(text)

        # GROUP 1
        if " ".join(map(str, doc.ents)) == text:
            if text.lower() not in allqueryset:
                groups[0].append(text)
                allqueryset.add(text.lower())
            # continue

        # GROUP 2
        NNPs = [str(tok) for tok in doc if tok.tag_ == "NNP"]
        if " ".join(NNPs) == text:
            if text.lower() not in allqueryset:
                groups[1].append(text)
                allqueryset.add(text.lower())
            # continue

        # GROUP 3
        if doc.ents:
            tmp = " ".join(map(str, doc.ents))
            if tmp.lower() not in allqueryset:
                groups[2].append(tmp)
                allqueryset.add(tmp.lower())

            # GROUP 4
            PERs = [str(tok) for tok in doc.ents if tok.label_ == "PERSON"]
            if PERs:
                tmp = max(PERs, key=len)
                if tmp.lower() not in allqueryset:
                    groups[3].append(tmp)
                    allqueryset.add(tmp.lower())
                # continue

            ORGs = [str(tok) for tok in doc.ents if tok.label_ == "ORG"]
            if ORGs:
                tmp = max(ORGs, key=len)
                if tmp.lower() not in allqueryset:
                    groups[3].append(tmp)
                    allqueryset.add(tmp.lower())
                # continue

        # GROUP 5
        NNPs = [str(tok) for tok in doc if tok.tag_ == "NNP"]
        if NNPs:
            tmp = " ".join(NNPs)
            if tmp.lower() not in allqueryset:
                groups[4].append(tmp)
                allqueryset.add(tmp.lower())

            # GROUP 6
            tmp = max(NNPs, key=len)
            if tmp.lower() not in allqueryset:
                groups[5].append(tmp)
                allqueryset.add(tmp.lower())

    return groups


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

        extracted_groups = extract_entity_groups(combined_trends)

        for group in extracted_groups:
            print(group)

        combined_results = []
        poswordset = set()

        for group in extracted_groups:
            group_results = []

            print("\n\n")
            print("#" * 100)
            print("#" * 100)
            print(group)

            for query in group:
                print("\n")
                print("#" * 100)
                # Call the rank_documents_bm25_bert function for each query
                if not query:
                    continue

                # if all words already covered in some previous search with results
                for word in query.lower().split():
                    if word not in poswordset:
                        break
                else:
                    print("Skipping:", query)
                    continue

                if not (query.startswith('"') and query.endswith('"')):
                    query = f'"{query}"'

                print(query)

                if not TEST_LOCAL:
                    # Create the request with the query wrapped in double quotes
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
                                group_results.append(
                                    {
                                        "query": query,
                                        "top_story_percentage": top_story_percentage,
                                        "result_data": result_data,
                                    }
                                )
                                poswordset.update(query[1:-1].lower().split())

                else:
                    idx, scores = model.rank(query)
                    percent = (
                        max(
                            list(scores[:3])
                            + [model.match_percent(query, origdata[idx[0]])]
                        )
                        if len(idx) > 0
                        else None
                    )
                    if len(idx) > 0:
                        group_results.append(
                            {
                                "query": query,
                                "top_story_percentage": percent,
                                "result_data": [origdata[x]["Headline"] for x in idx],
                            }
                        )
                        poswordset.update(query[1:-1].lower().split())
                        print(poswordset)

            # Sort combined results based on top story percentage
            sorted_results = sorted(
                group_results,
                # key=lambda x: x["top_story_percentage"],
                key=lambda x: len(x["query"]),
                reverse=True,
            )

            combined_results.extend(sorted_results)
            if len(combined_results) >= NUM_TRENDS:
                break

        # Get the top k queries with the highest match percentages
        top_k_results = combined_results[:NUM_TRENDS]

        # Prepare the response in the required format
        response_data = [
            {result["query"]: result["result_data"][:2]} for result in top_k_results
        ]

        # print(response_data)

        # Store the response data in a file
        with open("top_trends_cache.json", "w", encoding="utf-8") as cache_file:
            json.dump(response_data, cache_file, ensure_ascii=False, indent=4)
        print("Top trends stored successfully!")
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")


if TEST_LOCAL:
    fetch_and_store_top_trends()
