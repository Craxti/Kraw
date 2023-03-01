import argparse
import concurrent.futures
import requests
import time
import statistics
import logging
import matplotlib.pyplot as plt
from tqdm import tqdm

# Начало улучшений

DEFAULT_TIMEOUT = 5  # 5 секунд

def send_request(session, url, timeout):
    try:
        response = session.get(url, timeout=timeout)
        return response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for URL: {url}. Exception: {e}")
        return None

# Конец улучшений

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("test.log"),
            logging.StreamHandler()
        ]
    )

def print_stats(num_requests, success_set, failure_set, elapsed_time):
    num_success = len(success_set)
    num_failure = len(failure_set)
    success_rate = num_success / num_requests * 100
    logging.info(f"\nElapsed time: {elapsed_time:.2f} seconds")
    logging.info(f"Total requests: {num_requests}")
    logging.info(f"Successful requests: {num_success} ({success_rate:.2f}%)")
    logging.info(f"Failed requests: {num_failure} ({100 - success_rate:.2f}%)")
    if num_success > 0:
        logging.info(f"Fastest time: {min(success_set):.2f} seconds")
        logging.info(f"Slowest time: {max(success_set):.2f} seconds")
        logging.info(f"Average time: {statistics.mean(success_set):.2f} seconds")

def plot_results(success_set, failure_set):
    labels = ['Success', 'Failure']
    sizes = [len(success_set), len(failure_set)]
    colors = ['#00ff00', '#ff0000']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.show()

def run_test(url, num_requests, num_threads, test_time, timeout, plot=False):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    results_queue = concurrent.futures.Queue()
    success_set = set()
    failure_set = set()
    start_time = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_requests):
            executor.submit(send_request, session, url, timeout, results_queue)

        progress_bar = tqdm(total=num_requests * num_threads)
        while time.monotonic() - start_time < test_time:
            try:
                result = results_queue.get(timeout=1)
                progress_bar.update(1)
                if result:
                    success_set.add(result)
                else:
                    failure_set.add(result)
            except concurrent.futures.TimeoutError:
                pass

        progress_bar.close()

    elapsed_time = time.monotonic() - start_time
    print_stats(num_requests * num_threads, success_set, failure_set, elapsed_time)

    if plot:
        plot_results(success_set, failure_set)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Website stress testing tool')
    parser.add_argument('url', type=str, help='URL of the website to test')
    parser.add_argument('--requests', '-r', type=int, default=1000, help='Number of requests to send')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of threads to use')
    parser.add_argument('--time', '-s', type=int, default=60, help='Duration of the test in seconds')
    args = parser.parse_args()

    setup_logger()
    logging.info(f"Starting stress test for {args.url}")
    logging.info(f"Sending {args.requests} requests with {args.threads} threads for {args.time} seconds")
    run_test(args.url, args.requests, args.threads, args.time)
    logging.info("Stress test complete")
