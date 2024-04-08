from celery import shared_task
from django.conf import settings

from .scraper_handler import ScraperHandler

from .models import SearchByKeyword, Keyword, BookSearchByKeywordItem, GroupSearchByKeywordItem


@shared_task()
def good_reads_search_by_keyword_task(keyword, search_type=settings.GOOD_READS_DEFAULT_SEARCH_TYPE,
                                      page_count=settings.GOOD_READS_DEFAULT_SEARCH_PAGE_COUNT):
    print(f'good_reads_search_by_keyword_task => {keyword}({search_type}) Started')

    keyword, _ = Keyword.objects.get_or_create(
        title=keyword,
    )

    scraper_handler = ScraperHandler(
        base_url=settings.GOOD_READS_BASE_URL,
        search_url=settings.GOOD_READS_SEARCH_URL
    )

    search_by_keyword = SearchByKeyword.objects.create(
        keyword=keyword,
        search_type=search_type,
        page_count=page_count
    )
    scraped_item_count = scraper_handler.search_by_keyword(search_by_keyword_instance=search_by_keyword)

    print(f'good_reads_search_by_keyword_task => {keyword}({search_type}) finished')

    return {
        'keyword': keyword.title,
        'search_type': search_type,
        'page_count': page_count,
        'scraped_item_count': scraped_item_count,
        'status': 'finished',
    }


@shared_task()
def good_reads_scrape_remain_book_search_item():
    print('good_reads_scrape_remain_book_search_item => Started')

    remain_book_search_items = BookSearchByKeywordItem.objects.filter(is_scraped=False,).all()

    scraper_handler = ScraperHandler(
        base_url=settings.GOOD_READS_BASE_URL,
        search_url=settings.GOOD_READS_SEARCH_URL
    )

    new_scraped_item = list()

    for remain_book_search_item in remain_book_search_items:
        book, genres = scraper_handler.parse_book_detail(url=remain_book_search_item.url)
        remain_book_search_item.book = book
        remain_book_search_item.is_scraped = True
        remain_book_search_item.save()
        new_scraped_item.append(remain_book_search_item)

    print(new_scraped_item)

    print('good_reads_scrape_remain_book_search_item => finished')

    return {
        'new_scraped_item_count': len(new_scraped_item),
        'status': 'finished',
    }


@shared_task()
def good_reads_scrape_remain_group_search_item():
    print('good_reads_scrape_remain_group_search_item => Started')

    remain_group_search_items = GroupSearchByKeywordItem.objects.filter(is_scraped=False,).all()

    scraper_handler = ScraperHandler(
        base_url=settings.GOOD_READS_BASE_URL,
        search_url=settings.GOOD_READS_SEARCH_URL
    )

    new_scraped_item = list()

    for remain_group_search_item in remain_group_search_items:
        group = scraper_handler.parse_group_detail(url=remain_group_search_item.url)
        remain_group_search_item.group = group
        remain_group_search_item.is_scraped = True
        remain_group_search_item.save()
        new_scraped_item.append(remain_group_search_item)

    print(new_scraped_item)

    print('good_reads_scrape_remain_group_search_item => finished')

    return {
        'new_scraped_item_count': len(new_scraped_item),
        'status': 'finished',
    }

# celery -A good_reads_scraper_with_django worker -l INFO -P eventlet
# celery -A good_reads_scraper_with_django beat --loglevel=INFO