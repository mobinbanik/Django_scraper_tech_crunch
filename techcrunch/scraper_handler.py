import re

import requests
import bs4

from django.conf import settings

from .models import SearchedKeyword, SearchedPostByKeyword, Post, Author


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
            print(f"____ --- ||| PAGE {page} ||| --- ___")
            response = self.send_request(
                settings.SEARCH_URL_TECH_CRUNCH.format(
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

        print('|' * 50)
        print('posts found:')
        print(search_items)
        print('|' * 50)

        for i, search_item in enumerate(search_items, 1):
            self.get_json_and_create_post(search_item.post_slug)

    def extract_search_items(self, search_by_keyword, soup) -> SearchedPostByKeyword:
        search_items = list()

        posts_list = soup.find_all('a', attrs={'class': 'fz-20 lh-22 fw-b'})
        for i, post in enumerate(posts_list):
            title = post.text
            url = post.attrs['href']
            slug = self.parse_slug_from_url(url)
            search_items.append(
                SearchedPostByKeyword.objects.create(
                    title=title,
                    post_slug=slug,
                    url=url,
                    searched_by_keyword=search_by_keyword,
                    # TODO: ADD URL FOR THUMBNAIL
                )
            )
            print(i, ':', title)
            print(slug)
        return search_items

    def get_json_and_create_post(self, slug):
        print('GET A POST:')
        response = self.send_request(
            settings.POST_JSON_URL_BY_SLUG_TECH_CRUNCH.format(
                slug=slug,
                envelope=settings.ENVELOPE,
                embed=settings.EMBED,
            )
        )
        if response.status_code == 200:
            post_js = response.json()
            # print(post_js)
            # print('*' * 50)
            post_js = post_js['body'][0]
            id = post_js['id']
            slug = post_js['slug']
            title = post_js['title']['rendered']
            content = post_js['content']
            published_date = post_js['date']
            json = post_js
            # TODO: author_id = post_js['author']
            # TODO get and create author
            author, _ = Author.objects.get_or_create(
                full_name='mobin banikarim',
            )
            # TODO : thumbnail =
            post, flag = Post.objects.get_or_create(
                id=id,
                slug=slug,
                title=title,
                content=content,
                published_date=published_date,
                json=json,
                author=author,
            )
            print('*' * 50)
            print('*' * 50)
            print('*' * 50)
            print(flag)
            print('*' * 50)
            print('*' * 50)
            print('*' * 50)
            print(post)
            print('*' * 50)
        # TODO create Author
        # TODO IF STATUS CODE != 200 add it to failed

    @staticmethod
    def parse_slug_from_url(url) -> str:
        slug = re.findall('//techcrunch.com/.*/(.*)/$', url)
        return slug[0]

    def __str__(self):
        return "Scraper"
