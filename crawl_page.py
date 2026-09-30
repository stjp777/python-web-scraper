from crawl import get_html, extract_page_data, normalize_url
from urllib.parse import urljoin, urlsplit

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    if urlsplit(current_url).netloc != urlsplit(base_url).netloc:
        return page_data
    
    c_url = normalize_url(current_url)
    if c_url in page_data:
        return page_data
    
    print(f"Crawling: {current_url}")
    try:
        html = get_html(current_url)
        r_dict = extract_page_data(html, current_url)
        page_data[c_url] = r_dict

        for link in r_dict["outgoing_links"]:
            crawl_page(base_url, link, page_data)

        
    except Exception as e:
        print(f"Error fetching {current_url}: {e}")
        return page_data

    return page_data
    