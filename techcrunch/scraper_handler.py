import re
from http.client import HTTPException

import requests
import bs4

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from .models import (
    SearchedKeyword, SearchedPostByKeyword, Post, Author,
    ImagePost, ImageFile, FailedSearchedPosts, Category,
    PostCategory, FailedCategoryNewPosts,
)


class ScraperHandler:
    def __init__(self):
        pass

    def get_category_json_from_tech_crunch(self, category: Category):
        response = self.send_request(
            settings.CATEGORY_JSON_URL_TECH_CRUNCH.format(id=category.tech_crunch_id)
        )
        if response.status_code == 200:
            return response.json()

    def create_or_update_category_list(self, count):
        response = self.send_request(
            settings.ALL_CATEGORIES_JSON_URL_TECH_CRUNCH.format(
                count=count,
                envelope=settings.ENVELOPE_FALSE,
            )
        )
        categories = response.json()

        for category in categories:
            print(type(category["slug"]))
            cat, created = Category.objects.get_or_create(
                slug=category["slug"],
            )
            if created:
                cat.name = category["name"]
                cat.tech_crunch_id = category["id"]
                cat.description = category["description"]
                cat.json = category
                cat.save()
            elif not created:
                cat.json = category
                cat.save()

    def update_posts_for_all_categories(self):
        categories = Category.objects.all()
        for category in categories:
            self.update_posts_for_one_category(category)

    def update_posts_for_one_category(self, category):
        cat_js = self.get_category_json_from_tech_crunch(category)
        post_count_to_get = cat_js["count"]


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

        for search_item in search_items:
            print(search_item.post_slug)
            # try:
            self.get_json_and_create_post(search_item.post_slug)
            # except Exception as e:
            #     FailedSearchedPosts.objects.create(
            #         title=search_item.title,
            #         error_text=e.__str__(),
            #         searched_new_posts=search_item,
            #     )
            #     print(e)

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
                envelope=settings.ENVELOPE_TRUE,
                embed=settings.EMBED_TRUE,
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
            content = post_js['content']['rendered']
            published_date = post_js['date']
            json = post_js
            # TODO: author_id = post_js['author']
            # Get or create author
            author_js = post_js['_embedded']['author'][0]
            author, _ = Author.objects.get_or_create(
                full_name=author_js['name'],
                twitter_account=author_js['twitter'],
                json=author_js,
                slug=author_js['slug'],
            )
            # TODO : thumbnail =
            thumbnail_url = post_js['_embedded']['wp:featuredmedia'][0]['source_url']
            thumbnail, _ = ImageFile.objects.get_or_create(
                url=thumbnail_url,
                file_name=self.parse_image_name_from_url(thumbnail_url),
                post_id=id,
                is_scraped=False,
            )
            self.get_image_file_from_url(thumbnail_url, thumbnail)
            post, flag = Post.objects.get_or_create(
                id=id,
                slug=slug,
                title=title,
                content=content,
                published_date=published_date,
                json=json,
                author=author,
                thumbnail=thumbnail,
            )
            self.extract_image_from_content(content, post)
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

    @staticmethod
    def parse_image_name_from_url(url) -> str:
        name = re.findall('//techcrunch.com/.*/(.*\.[a-z]*).*$', url)
        print(1000*'"')
        print(name)
        print(url)
        return name[0]

    def extract_image_from_content(self, content: str, post: Post):
        soup = bs4.BeautifulSoup(content, 'html.parser')
        images = soup.find_all('img')

        for i, image in enumerate(images):
            src = image['src']
            image_file, _ = ImageFile.objects.get_or_create(
                url=src,
                file_name=self.parse_image_name_from_url(src),
                post_id=post.id,
                is_scraped=True,
            )
            self.get_image_file_from_url(src, image_file)
            image_post, _ = ImagePost.objects.get_or_create(
                post=post,
                image=image_file,
                image_order=i,
                title=post.title,
            )

    @staticmethod
    def get_image_file_from_url(url: str, image_file: ImageFile):
        response = requests.get(url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        img_temp.name = image_file.file_name
        image_file.image.save("image.jpg", File(img_temp), save=True)
        img_temp.close()

    def __str__(self):
        return "Scraper"
