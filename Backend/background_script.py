from background_tasks import fetch_and_store_top_trends

if __name__ == "__main__":
    print("Starting scheduler...")
    fetch_and_store_top_trends()
