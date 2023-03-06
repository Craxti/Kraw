import requests
from bs4 import BeautifulSoup
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import pymongo
import re
from urllib.robotparser import RobotFileParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio
import aiohttp

visited_pages = []

def get_robots_txt(url):
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    return rp

def is_allowed(url, rp):
    return rp.can_fetch("*", url)

async def fetch_url(session, url):
    async with session.get(url) as response:
        try:
            content_type = response.headers['Content-Type']
            if content_type.startswith('text/html'):
                html = await response.text()
                return url, html
        except:
            pass
    return None, None

async def process_links(loop, db, rp, links):
    async with aiohttp.ClientSession(loop=loop) as session:
        tasks = []
        for link in links:
            url = link['href']
            if url.startswith('http') and urlparse(url).netloc != "":
                task = loop.create_task(fetch_url(session, url))
                tasks.append(task)
        for task in as_completed(tasks):
            url, html = await task
            if url and html:
                data = {"url": url, "html": html}
                db.pages.insert_one(data)

def crawl(url, depth, max_pages, db, rp):
    # Проверяем, была ли эта страница посещена ранее или достигнута максимальная глубина
    if url in visited_pages or depth == 0 or len(visited_pages) == max_pages:
        return
    # Проверяем, разрешено ли посещение страницы
    if not is_allowed(url, rp):
        print(f"Запрещено посещение страницы: {url}")
        return
    # Добавляем страницу в список посещенных
    visited_pages.append(url)
    # Отправляем GET-запрос на URL
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка: {e}")
        return
    # Используем BeautifulSoup для извлечения ссылок на странице
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)
    # Обрабатываем ссылки асинхронно
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_links(loop, db, rp, links))
    loop.close()
    # Снижаем глубину на 1 и рекурсивно обрабатываем каждую ссылку
    for link in links:
        href = link.get("href")
        if href.startswith("http"):
            crawl(href, depth - 1, max_pages, db, rp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web crawler")
    parser.add_argument("url", help="Starting URL")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth")
    parser.add_argument("-p", "--max_pages", type=int, default=10, help="Maximum number of pages to crawl")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="Number of concurrent requests")
    args = parser.parse_args()

    # Инициализируем базу данных MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["crawler"]
    db.pages.drop()
    db.pages.create_index("url", unique=True)

    # Получаем robots.txt для начального URL
    rp = get_robots_txt(args.url)

    # Запускаем краулер
    crawl(args.url, args.depth, args.max_pages, db, rp)

# Выводим результаты
print(f"Visited {len(visited_pages)} pages")
