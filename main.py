import asyncio
import sys

from crawl import crawl_site_async
from json_report import write_json_report


async def main():
  if len(sys.argv) < 4:
    print("Usage: uv run main.py <url> <max_concurrency> <max_pages>")
    sys.exit(1)

  if len(sys.argv) > 4:
    print("too many arguments provided")
    sys.exit(1)

  base_url = sys.argv[1]
  print(f"starting crawl of: {base_url}")

  max_concurrency = int(sys.argv[2])
  max_pages = int(sys.argv[3])

  pages = await crawl_site_async(base_url, max_concurrency, max_pages)

  print(f"\nCrawled a total of {len(pages)} pages.\n")
  
  write_json_report(pages)


if __name__ == "__main__":
  asyncio.run(main())