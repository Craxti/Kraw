import requests
import threading
import queue
from typing import List, Tuple

NUM_THREADS = 10  # количество потоков
NUM_REQUESTS = 100  # количество запросов
TIMEOUT = 5  # таймаут для запросов в секундах
URLS_FILE = 'urls.txt'  # файл со списком URL-адресов
PROXIES = {'http': 'http://localhost:8080', 'https': 'http://localhost:8080'}  # прокси-сервер
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

class RequestWorker(threading.Thread):
    """Класс для работы с запросами в отдельном потоке"""
    def __init__(self, queue: queue.Queue, result_queue: queue.Queue, headers: dict):
        super().__init__()
        self.queue = queue
        self.result_queue = result_queue
        self.headers = headers

    def run(self) -> None:
        while True:
            # Получаем URL из очереди
            url = self.queue.get()
            try:
                # Отправляем запрос
                response = requests.get(url, timeout=TIMEOUT, proxies=PROXIES, headers=self.headers)
                # Добавляем результат в очередь результатов
                self.result_queue.put((url, response.status_code))
            except requests.exceptions.RequestException:
                # Если произошла ошибка, добавляем None в очередь результатов
                self.result_queue.put((url, None))
            finally:
                # Уменьшаем значение счетчика
                self.queue.task_done()

def stress_test(urls: List[str], num_threads: int = NUM_THREADS) -> List[Tuple[str, int]]:
    # Создаем очереди для URL-адресов и результатов
    urls_queue = queue.Queue()
    result_queue = queue.Queue()

    # Заполняем очередь URL-адресами из списка
    for url in urls:
        urls_queue.put(url)

    # Запускаем потоки-работники
    for i in range(num_threads):
        t = RequestWorker(urls_queue, result_queue, headers=HEADERS)
        t.daemon = True
        t.start()

    # Ждем, пока все URL будут обработаны
    urls_queue.join()

    # Получаем результаты из очереди результатов
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    # Сортируем результаты по URL-адресам
    results = sorted(results, key=lambda x: x[0])

    return results

if __name__ == '__main__':
    # Читаем URL-адреса из файла
    with open(URLS_FILE) as f:
        urls = f.read().splitlines()

    # Запускаем тестирование
    results = stress_test(urls)

    # Выводим результаты
    for url, status_code in results:
        if status_code is None:
            print(f"{url}: Request failed")
        else:
            print(f"{url}: Status code {status_code}")
