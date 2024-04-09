from celery import shared_task
from django.conf import settings

from .scraper_handler import ScraperHandler

from .models import Keyword, SearchedKeyword, SearchedPostByKeyword, FailedSearchedPosts


@shared_task()
def tech_crunch_search_by_keyword_task(
        keyword: str,
        page_count=settings.DEFAULT_SEARCH_PAGE_COUNT_TECH_CRUNCH,
):
    print(f'tech_crunch_search_by_keyword_task => {keyword} Started')

    keyword, _ = Keyword.objects.get_or_create(
        title=keyword,
    )
    search_by_keyword_instance = SearchedKeyword.objects.create(
        title=keyword.title,
        keyword=keyword,
        page_count=page_count,
    )

    scraper_handler = ScraperHandler()

    scraped_item_count = len(
        scraper_handler.search_by_keyword(search_by_keyword_instance)
    )
    print(f'tech_crunch_search_by_keyword_task => {keyword} finished')

    return {
        'keyword': keyword.title,
        'page_count': page_count,
        'scraped_item_count': scraped_item_count,
        'status': 'finished',
    }


@shared_task()
def tech_crunch_scrape_remain_post_search_item():
    print('tech_crunch_scrape_remain_post_search_item => Started')

    post_search_items = SearchedPostByKeyword.objects.filter(
        is_scraped=False,
    ).all()

    scraper_handler = ScraperHandler()

    new_scraped_item = list()

    for post_search_item in post_search_items:
        try:
            post = scraper_handler.get_json_and_create_post_by_slug(
                post_search_item.post_slug
            )
            post_search_item.post = post
            post_search_item.is_scraped = True
            post_search_item.save()
            new_scraped_item.append(post_search_item)
        except Exception as e:
            FailedSearchedPosts.objects.create(
                title=post_search_item.title,
                error_text=e.__str__(),
                searched_new_posts=post_search_item,
            )
            # TODO: add log
            print(e)

    print(new_scraped_item)
    print('tech_crunch_scrape_remain_post_search_item => finished')

    return {
        'new_scraped_item_count': len(new_scraped_item),
        'status': 'finished',
    }


@shared_task()
def tech_crunch_create_or_update_all_categories():
    print('tech_crunch_create_or_update_all_categories => Started')
    scraper_handler = ScraperHandler()
    created, updated = scraper_handler.create_or_update_category_list(settings.DEFAULT_CATEGORY_COUNT_UPDATE)
    print('tech_crunch_create_or_update_all_categories => finished')
    return {
        'category_created_count': created,
        'category_updated_count': updated,
        'status': 'finished',
    }


@shared_task()
def tech_crunch_update_posts_for_all_categories():
    print('tech_crunch_update_posts_for_all_categories => Started')
    scraper_handler = ScraperHandler()
    count = scraper_handler.update_posts_for_all_categories()
    print('tech_crunch_update_posts_for_all_categories => finished')
    return {
        'post_count': count,
        'status': 'finished',
    }

# celery -A techcrunch_scraper worker -l INFO -P eventlet
# celery -A techcrunch_scraper beat --loglevel=INFO
