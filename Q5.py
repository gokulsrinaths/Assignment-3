import urllib.request
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawlerdb"]
pages_collection = db["pages"]

class Frontier:
    def __init__(self):
        self.to_visit = []
        self.visited = set()
        self.done_flag = False

    def add_url(self, url):
        """Adds a URL to the list of URLs to visit if it's not already visited or queued."""
        if url not in self.visited and url not in self.to_visit:
            self.to_visit.append(url)

    def next_url(self):
        """Gets the next URL from the list and marks it as visited."""
        if self.to_visit:
            url = self.to_visit.pop(0)
            self.visited.add(url)
            return url
        return None

    def done(self):
        """Checks if there are no URLs left to visit or if the crawling is marked as done."""
        return self.done_flag or not self.to_visit

    def clear_frontier(self):
        """Clears the frontier, indicating the crawl is complete."""
        self.to_visit = []
        self.done_flag = True

def retrieve_html(url):
    """Retrieves HTML content from a URL."""
    try:
        response = urllib.request.urlopen(url)
        content_type = response.headers.get('Content-Type')
        if 'text/html' in content_type:
            html = response.read()
            return html
        return None
    except Exception as e:
        print(f"Failed to retrieve {url}: {e}")
        return None

def store_page(url, html):
    """Stores the HTML content of a page in MongoDB."""
    pages_collection.insert_one({'url': url, 'html': html.decode('utf-8')})

def parse_links(html, base_url):
    """Parses the HTML to extract all relevant links within the base domain."""
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)
        
        if parsed_url.scheme in ['http', 'https']:
            path = parsed_url.path
            if (path.endswith('.html') or path.endswith('.shtml') or path.endswith('.htm') or path == '' or path.endswith('/')) \
               and absolute_url.startswith('https://www.cpp.edu/sci/computer-science/'):
                urls.append(absolute_url)
    return urls

def is_target_page(html):
    """Checks if the page contains the target header indicating the target page."""
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.find('h1', class_='cpp-h1')
    return h1 and h1.text.strip() == 'Permanent Faculty'

def flag_target_page(url):
    """Flags that the target page has been found."""
    print(f"Target page found: {url}")

def crawler_thread(frontier):
    """The main crawler function that processes URLs in the frontier."""
    while not frontier.done():
        url = frontier.next_url()
        if url is None:
            break
        print(f"Visiting: {url}")
        html = retrieve_html(url)
        if html:
            store_page(url, html)
            if is_target_page(html):
                flag_target_page(url)
                frontier.clear_frontier()
            else:
                urls = parse_links(html, url)
                for link in urls:
                    frontier.add_url(link)

if __name__ == "__main__":
    start_url = 'https://www.cpp.edu/sci/computer-science/'
    frontier = Frontier()
    frontier.add_url(start_url)
    crawler_thread(frontier)

