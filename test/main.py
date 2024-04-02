from scraper_handler import ScraperHandler
from constant import DEFAULT_SEARCH_PAGE_COUNT_TECH_CRUNCH

keyword = input("Keyword:") or 'art'
page_count = int(input("Page:") or DEFAULT_SEARCH_PAGE_COUNT_TECH_CRUNCH)

scraper_handler = ScraperHandler()

scraper_handler.search_by_keyword(keyword=keyword, page_count=page_count)
