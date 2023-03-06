import unittest
import pymongo

from crawler import get_links, get_robots_txt, get_page, crawl


class TestCrawler(unittest.TestCase):

    def setUp(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["crawler"]
        self.db.pages.drop()
        self.db.pages.create_index("url", unique=True)

    def test_get_links(self):
        html = """
        <html>
            <body>
                <a href="https://example.com/page1.html">Page 1</a>
                <a href="https://example.com/page2.html">Page 2</a>
                <a href="https://example.com/page3.html">Page 3</a>
            </body>
        </html>
        """
        links = get_links(html, "https://example.com")
        self.assertEqual(links, [
            "https://example.com/page1.html",
            "https://example.com/page2.html",
            "https://example.com/page3.html",
        ])

    def test_get_robots_txt(self):
        rp = get_robots_txt("https://www.google.com/")
        self.assertIsNotNone(rp)
        self.assertIn("User-agent", rp)

    def test_get_page(self):
        page = get_page("https://www.google.com/")
        self.assertIsNotNone(page)
        self.assertIn("<html", page)

    def test_crawl(self):
        self.maxDiff = None
        crawl("https://en.wikipedia.org/wiki/Python_(programming_language)", 2, 10, self.db, None)
        pages = list(self.db.pages.find())
        self.assertGreater(len(pages), 0)
        self.assertLessEqual(len(pages), 10)

    def tearDown(self):
        self.client.drop_database("crawler")


if __name__ == '__main__':
    unittest.main()

