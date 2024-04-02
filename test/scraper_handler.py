import re

import requests
import bs4

from constant import SEARCH_URL_TECH_CRUNCH, POST_JSON_URL_BY_SLUG_TECH_CRUNCH


class ScraperHandler:
    def __init__(self):
        pass

    @staticmethod
    def send_request(url) -> requests.Response:
        print('URL: ', url)
        return requests.get(url)

    def search_by_keyword(self, keyword: str, page_count: int):
        for page in range(page_count):
            response = self.send_request(
                SEARCH_URL_TECH_CRUNCH.format(keyword=keyword, page=page)
            )
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            # find list
            posts_list = soup.find_all('a', attrs={'class': 'fz-20 lh-22 fw-b'})
            for i, post in enumerate(posts_list):
                title = post.text
                url = post.attrs['href']
                slug = self.parse_slug_from_url(url)
                print(i, ':', title)
                print(slug)
                # TODO create PostSearchedByKeyword(BaseModel)
                self.get_and_save_posts(slug)

    def get_and_save_posts(self, slug):
        response = self.send_request(POST_JSON_URL_BY_SLUG_TECH_CRUNCH.format(
            slug=slug,
            envelope='false',
            embed='true',
        ))
        post_js = response.json()
        post_js = post_js['body'][0]
        title = post_js['title']['rendered']
        post_id = post_js['id']
        # TODO create Author


    @staticmethod
    def parse_slug_from_url(url) -> str:
        slug = re.findall('//techcrunch.com/.*/(.*)/$', url)
        return slug[0]

    def __str__(self):
        return "Scraper"
