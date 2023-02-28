import argparse
import concurrent.futures
import requests
import time
import statistics

def send_request(session, url):
    try:
        response = session.get(url)
        return response.status_code
    except requests.exceptions.RequestException:
        return None

def print_stats(num_requests, success_set, failure_set, elapsed_time):
    num_success = len(success_set)
    num_failure = len(failure_set)
    success_rate = num_success / num_requests * 100
    print(f"\nElapsed time: {elapsed_time:.2f} seconds")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {num_success} ({success_rate:.2f}%)")
    print(f"Failed requests: {num_failure} ({100 - success_rate:.2f}%)")
    if num_success > 0:
        print(f"Fastest time: {min(success_set):.2f} seconds")
        print(f"Slowest time: {max(success_set):.2f} seconds")
        print(f"Average time: {statistics.mean(success_set):.2f} seconds")

def run_test(url, num_requests, num_threads, test_time):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    results_queue = concurrent.futures.Queue()
    success_set = set()
    failure_set = set()
    start_time = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_requests):
            executor.submit(send_request, session, url, results_queue)

        while time.monotonic() - start_time < test_time:
            try:
                result = results_queue.get(timeout=1)
                if result:
                    success_set.add(result)
                else:
                    failure_set.add(result)
            except concurrent.futures.TimeoutError:
                pass

    elapsed_time = time.monotonic() - start_time
    print_stats(num_requests * num_threads, success_set, failure_set, elapsed_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Website stress testing tool')
    parser.add_argument('url', type=str, help='URL of the website to test')
    parser.add_argument('--requests', '-r', type=int, default=1000, help='Number of requests to send')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of threads to use')
    parser.add_argument('--time', '-s', type=int, default=60, help='Duration of the test in seconds')
    args = parser.parse_args()

    run_test(args.url, args.requests, args.threads, args.time)
