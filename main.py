import requests
import threading
import time

# Функция отправки запросов
def send_request(url, method, data=None, headers=None, cookies=None):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, cookies=cookies)
        elif method == "POST":
            response = requests.post(url, data=data, headers=headers, cookies=cookies)
        else:
            response = requests.get(url, headers=headers, cookies=cookies)

        response.raise_for_status()
        print(f"Request to {url} successful with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")

# Функция для запуска потоков для отправки запросов
def run_threads(num_threads, urls, method, data=None, headers=None, cookies=None):
    # Определение максимального количества потоков для выполнения запросов
    max_threads = min(num_threads, len(urls))

    # Создание списка потоков для отправки запросов
    threads = []

    # Запуск потоков для отправки запросов
    start_time = time.time()
    for i in range(max_threads):
        thread_urls = urls[i::max_threads] # равномерное распределение запросов по потокам
        thread = threading.Thread(target=send_request, args=(thread_urls, method, data, headers, cookies))
        threads.append(thread)
        thread.start()

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

    # Время выполнения теста
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Completed {len(urls)} requests in {total_time:.2f} seconds with {max_threads} threads.")

# Функция для выполнения стресс-теста веб-сервиса
def stress_test(url, num_requests=100, method="GET", num_threads=32, data=None, headers=None, cookies=None):
    # Создание списка URL для отправки запросов
    urls = [url] * num_requests

    # Запуск потоков для отправки запросов
    run_threads(num_threads, urls, method, data, headers, cookies)

    

url = "https://www.example.com"
num_requests = 100
method = "GET"
num_threads = 32
data = None
headers = {"User-Agent": "Mozilla/5.0"}
cookies = {"sessionid": "1234567890abcdef"}

stress_test(url, num_requests, method, num_threads, data, headers, cookies)
