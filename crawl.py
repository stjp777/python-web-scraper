from bs4 import BeautifulSoup, Tag
from urllib.parse import urlsplit, urljoin
from typing import TypedDict
import asyncio, aiohttp

def normalize_url(url):
    u = urlsplit(url)
    return f"{u.netloc}{u.path}"

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1")
    if heading is None:
        heading = soup.find("h2")
        if heading is None:
            return ""
    return heading.get_text(strip=True)

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    p = main.find("p") if main else None
    if p is None:
        p = soup.find("p")
    return p.get_text(strip=True) if p else ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    urlss = []
    urls = soup.find_all("a", href=True)
    for tag in urls:
        href = tag.get("href")
        joined = urljoin(base_url, href)
        urlss.append(joined)
    return urlss

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    images = []
    img_tags = soup.find_all("img", src=True)
    for tag in img_tags:
        src = tag.get("src")
        joined = urljoin(base_url, src)
        images.append(joined)
    return images

def extract_page_data(html: str, page_url: str):
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


class AsyncCrawler():
    def __init__(self, base_url, max_pages, max_concurrency):
        self.base_url = base_url
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

        self.base_domain = urlsplit(base_url).netloc
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):   
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop == True:
                return False

            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False

            if normalized_url in self.visited:
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url):
        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
            if response.status >= 400:
                raise Exception(f"Error fetching {url}: {response.status}")
            if "text/html" not in response.headers.get("Content-Type", ""):
                raise Exception(f"Error fetching {url}: not HTML")
            return await response.text()

    async def crawl_page(self, current_url: str):

        if self.should_stop:
            return

        c_url = normalize_url(current_url)
        if not await self.add_page_visit(c_url):
            return

        print(f"Crawling: {current_url}")

        try:
            async with self.semaphore:
                html = await self.get_html(current_url)
                r_dict = extract_page_data(html, current_url)
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            return

        async with self.lock:
            self.page_data[c_url] = r_dict

        tasks = []
        
        for link in r_dict["outgoing_links"]:
            if urlsplit(link).netloc == self.base_domain:
                task = asyncio.create_task(self.crawl_page(link))
                self.all_tasks.add(task)
                tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)
        

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url, max_concurrency=5, max_pages=100):
    async with AsyncCrawler(base_url, max_pages, max_concurrency) as crawler:
        return await crawler.crawl()