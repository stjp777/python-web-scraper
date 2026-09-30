import unittest
from crawl import extract_page_data, normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)
    
    def test_get_heading_from_html_h1(self):
        html = "<html><body><h1>Main Title</h1></body></html>"
        self.assertEqual(get_heading_from_html(html), "Main Title")

    def test_get_heading_from_html_h2_fallback(self):
        html = "<html><body><h2>Subheading</h2></body></html>"
        self.assertEqual(get_heading_from_html(html), "Subheading")

    def test_get_heading_from_html_none(self):
        html = "<html><body><p>No headings here</p></body></html>"
        self.assertEqual(get_heading_from_html(html), "")

    # 📄 Paragraph tests
    def test_get_first_paragraph_main_priority(self):
        html = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        self.assertEqual(get_first_paragraph_from_html(html), "Main paragraph.")

    def test_get_first_paragraph_fallback(self):
        html = "<html><body><p>Only paragraph.</p></body></html>"
        self.assertEqual(get_first_paragraph_from_html(html), "Only paragraph.")

    def test_get_first_paragraph_none(self):
        html = "<html><body><h1>Just a heading</h1></body></html>"
        self.assertEqual(get_first_paragraph_from_html(html), "")

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><a href="https://crawler-test.com/about"><span>About</span></a></body></html>'
        self.assertEqual(
            get_urls_from_html(html, base_url),
            ["https://crawler-test.com/about"],
        )

    def test_get_urls_from_html_relative(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><a href="/path/one">Link 1</a><a href="/path/two">Link 2</a></body></html>'
        self.assertEqual(
            get_urls_from_html(html, base_url),
            ["https://crawler-test.com/path/one", "https://crawler-test.com/path/two"],
        )

    def test_get_urls_from_html_missing_href(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><a href="/valid">Valid</a><a>No Link</a></body></html>'
        self.assertEqual(
            get_urls_from_html(html, base_url),
            ["https://crawler-test.com/valid"],
        )

    # 🖼️ Image extraction tests
    def test_get_images_from_html_relative(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        self.assertEqual(
            get_images_from_html(html, base_url),
            ["https://crawler-test.com/logo.png"],
        )

    def test_get_images_from_html_multiple(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><img src="/cat.jpg"><img src="https://other.com/dog.png"></body></html>'
        self.assertEqual(
            get_images_from_html(html, base_url),
            ["https://crawler-test.com/cat.jpg", "https://other.com/dog.png"],
        )

    def test_get_images_from_html_missing_src(self):
        base_url = "https://crawler-test.com"
        html = '<html><body><img alt="Broken image"><img src="/banner.webp"></body></html>'
        self.assertEqual(
            get_images_from_html(html, base_url),
            ["https://crawler-test.com/banner.webp"],
        )

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)


    def test_extract_page_data_empty_content(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)


    def test_extract_page_data_fallbacks(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Fallback Heading</h2>
            <main>
                <p>Main body paragraph.</p>
            </main>
            <a href="https://other.com/page">External</a>
            <img src="https://other.com/pic.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Fallback Heading",
            "first_paragraph": "Main body paragraph.",
            "outgoing_links": ["https://other.com/page"],
            "image_urls": ["https://other.com/pic.png"],
        }
        self.assertEqual(actual, expected)


    def test_get_first_paragraph_from_html_main_priority(self):
            input_body = """<html><body>
                <p>Outside paragraph.</p>
                <main>
                    <p>Main paragraph.</p>
                </main>
            </body></html>"""
            actual = get_first_paragraph_from_html(input_body)
            expected = "Main paragraph."
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()