# Web Crawler

This is a simple web crawler written in Python. It uses aiohttp for asynchronous HTTP requests, BeautifulSoup for HTML parsing, and MongoDB for storing crawled pages.

## Usage

To run the crawler, first install the dependencies:

`pip install -r requirements.txt`

Then run the `crawler.py` script

`python crawler.py -u https://example.com -d 2 -p 10 -c 10`

The options are as follows:

- `-u` or `--url`: the starting URL
- `-d` or `--depth`: the maximum depth to crawl (default is 2)
- `-p` or `--max_pages`: the maximum number of pages to crawl (default is 10)
- `-c` or `--concurrency`: the number of concurrent requests (default is 10)

## Docker

To run the crawler in a Docker container, build the image:

`docker build -t web-crawler `

Then run the container:

`docker run -it --rm web-crawler -u https://example.com -d 2 -p 10 -c 10`
