import re

import requests
import bs4

from constant import SEARCH_URL_TECH_CRUNCH, POST_JSON_URL_BY_SLUG_TECH_CRUNCH

from .models import SearchedKeyword, SearchedPostByKeyword


class ScraperHandler:
    def __init__(self):
        pass

    @staticmethod
    def send_request(url) -> requests.Response:
        print('URL: ', url)
        return requests.get(url)

    def search_by_keyword(self, search_by_keyword: SearchedKeyword):
        search_items = list()

        for page in range(search_by_keyword.page_count):
            response = self.send_request(
                SEARCH_URL_TECH_CRUNCH.format(
                    keyword=search_by_keyword.keyword,
                    page=page,
                )
            )
            # extract all items in the page
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, 'html.parser')
                search_items += self.extract_search_items(
                    search_by_keyword,
                    soup,
                )


            self.get_and_save_posts(slug)

    def extract_search_items(self, search_by_keyword, soup):
        search_items = list()

        posts_list = soup.find_all('a', attrs={'class': 'fz-20 lh-22 fw-b'})
        for i, post in enumerate(posts_list):

            title = post.text
            url = post.attrs['href']
            slug = self.parse_slug_from_url(url)
            search_items.append(
                SearchedPostByKeyword(
                    title=title,
                    post_slug=slug,
                    url=url,
                    searched_by_keyword=search_by_keyword,
                )
            )
            print(i, ':', title)
            print(slug)
            # TODO create PostSearchedByKeyword(BaseModel)

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
