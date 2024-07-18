import aiohttp
import asyncio
import time
import matplotlib.pyplot as plt


async def post_request(session, url, data, index):
    start_time = time.time()
    async with session.post(url, json=data, ssl=False) as response:
        response_text = await response.text()
    end_time = time.time()
    duration = end_time - start_time
    return response_text, duration


async def run_batch(url, data, num_requests):
    async with aiohttp.ClientSession() as session:
        tasks = [
            post_request(session, url, data, i) for i in range(1, num_requests + 1)
        ]
        responses = await asyncio.gather(*tasks)
    return responses


async def measure_time(url, data, num_requests_list):
    results = []
    for num_requests in num_requests_list:
        start_time = time.time()
        await run_batch(url, data, num_requests)
        end_time = time.time()
        total_duration = end_time - start_time
        results.append((num_requests, total_duration))
        print(f"Total time for {num_requests} requests: {total_duration:.2f} seconds")
    return results


def plot_results(results):
    num_requests, durations = zip(*results)
    plt.figure(figsize=(10, 6))
    plt.plot(num_requests, durations, marker="o")
    plt.title("Time Taken to Process Different Numbers of Concurrent Requests")
    plt.xlabel("Number of Concurrent Requests")
    plt.ylabel("Time Taken (seconds)")
    plt.grid(True)
    plt.show()


async def main():
    url = "https://factcheckerbtp.vishvasnews.com/api/ensemble"
    data = {"query": "Rahul Gandhi"}
    num_requests_list = [1, 5, 10, 20, 30, 40, 50]
    results = await measure_time(url, data, num_requests_list)
    plot_results(results)


if __name__ == "__main__":
    asyncio.run(main())
