import requests
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Функция отправки запросов
def send_request(url, method, data=None, headers=None, cookies=None, verify_ssl=True, timeout=None, max_retries=1):
    try:
        retries = 0
        while retries < max_retries:
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, cookies=cookies, verify=verify_ssl, timeout=timeout)
                elif method == "POST":
                    response = requests.post(url, data=data, headers=headers, cookies=cookies, verify=verify_ssl, timeout=timeout)
                else:
                    response = requests.get(url, headers=headers, cookies=cookies, verify=verify_ssl, timeout=timeout)

                response.raise_for_status()
                return url, response.status_code
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries == max_retries:
                    return url, str(e)
                else:
                    time.sleep(1)

# Функция для запуска потоков для отправки запросов
def run_threads(num_threads, urls, method, data=None, headers=None, cookies=None, verify_ssl=True, timeout=None, max_retries=1):
    # Определение максимального количества потоков для выполнения запросов
    max_threads = min(num_threads, len(urls))

    # Создание пула потоков для отправки запросов
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        # Запуск потоков для отправки запросов
        for url in urls:
            future = executor.submit(send_request, url, method, data, headers, cookies, verify_ssl, timeout, max_retries)
            futures.append(future)

        # Ожидание завершения всех потоков и сбор результатов
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    return results

# Функция для выполнения стресс-теста веб-сервиса
def stress_test(url, num_requests=100, method="GET", num_threads=32, data=None, headers=None, cookies=None, verify_ssl=True, timeout=None, max_retries=1, delay=None, random_delay=False):
    # Создание списка URL для отправки запросов
    urls = [url] * num_requests

    # Добавление задержки между запросами (если указана)
    if delay is not None:
        if random_delay:
            delays = [random.uniform(delay[0], delay[1]) for i in range(num_requests)]
        else:
            delays = [delay] * num_requests
        time.sleep(delay)

   # Запуск потоков для отправки запросов
start_time = time.time()
results = run_threads(num_threads, urls, method, data, headers, cookies, verify_ssl, timeout, max_retries)
end_time = time.time()

# Время выполнения теста
total_time = end_time - start_time

# Вывод результатов теста
num_success = 0
num_errors = 0
error_codes = {}
for result in results:
    url, status_code = result
    if isinstance(status_code, int):
        num_success += 1
    else:
        num_errors += 1
        if status_code in error_codes:
            error_codes[status_code] += 1
        else:
            error_codes[status_code] = 1

print(f"Stress test results for {url}:")
print(f"Total requests: {num_requests}")
print(f"Successful requests: {num_success}")
print(f"Failed requests: {num_errors}")
print(f"Total time: {total_time:.2f} seconds")

if num_errors > 0:
    print("Error codes:")
    for code, count in error_codes.items():
        print(f"{code}: {count}")
        
        
def generate_random_url():
    protocols = ["http", "https"]
    tlds = ["com", "net", "org", "info", "biz", "ru", "io", "app"]
    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine", "orange", "peach", "quince", "raspberry", "strawberry", "tangerine", "watermelon"]
    protocol = random.choice(protocols)
     domain = f"{random.choice(words)}.{random.choice(tlds)}"
    return f"{protocol}://{domain}"

if name == "main":
    # Генерация случайных URL-адресов для тестирования
    urls = [generate_random_url() for i in range(100)] 
    # Выполнение стресс-теста
    stress_test(url=urls[0], num_requests=1000, num_threads=64)
