import schedule
import time
from background_tasks import fetch_and_store_top_trends


def run_scheduler():
    print("Starting scheduler...")
    # # Schedule the task to run at 11 AM and 6 PM every day
    # schedule.every().day.at("7:00").do(fetch_and_store_top_trends)
    # print("Scheduled 7:00")
    schedule.every().day.at("11:00").do(fetch_and_store_top_trends)
    print("Scheduled 11:00")
    schedule.every().day.at("12:00").do(fetch_and_store_top_trends)
    print("Scheduled 12:00")
    schedule.every().day.at("17:00").do(fetch_and_store_top_trends)
    print("Scheduled 17:00")
    schedule.every().day.at("23:00").do(fetch_and_store_top_trends)
    print("Scheduled 23:00")
    # Run the task once when the server starts
    fetch_and_store_top_trends()

    while True:
        schedule.run_pending()
        time.sleep(1)
