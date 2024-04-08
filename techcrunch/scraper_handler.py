import re
import logging

import requests
import bs4

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from .models import (
    SearchedKeyword, SearchedPostByKeyword, Post, Author,
    ImagePost, ImageFile, FailedSearchedPosts, Category,
    PostCategory, FailedCategoryNewPosts, DailySearch,
    PostDailySearch, ScrapedPosts, ScrapedPostsCategory,
)


class ScraperHandler:
    def __init__(self):
        print("Initializing ScraperHandler")
        # TODO: ADD LOG
        # logging

    @staticmethod
    def send_request(url) -> requests.Response:
        print('URL: ', url)
        return requests.get(url)

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
            daily_search = DailySearch.objects.create(
                category=category,
                title=category.name,
            )
            try:
                self.update_posts_for_one_category(category, daily_search)
            except Exception as e:
                FailedCategoryNewPosts.objects.create(
                    daily_search=daily_search,
                    title=category.name,
                    error_text=e.__str__(),
                )

    def update_posts_for_one_category(self, category, daily_search: DailySearch):
        cat_js = self.get_category_json_from_tech_crunch(category)
        post_count_to_get = cat_js["count"] - category.online_post_count()
        print(post_count_to_get)
        if post_count_to_get > 0:
            response = self.send_request(
                settings.POST_BY_CATEGORY_URL_TECH_CRUNCH.format(
                    category_id=category.tech_crunch_id,
                    per_page=post_count_to_get,
                    page=1,
                    envelope=settings.ENVELOPE_FALSE,
                    embed=settings.EMBED_TRUE,
                )
            )
            posts = response.json()
            for post in posts:
                temp_post = self.parse_post_json(post)
                PostDailySearch.objects.create(
                    daily_search=daily_search,
                    post=temp_post,
                )
            category.json = cat_js
            category.save()

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

        # TODO: Without Celery
        for search_item in search_items:
            try:
                post = self.get_json_and_create_post_by_slug(
                    search_item.post_slug
                )
                search_item.post = post
                search_item.is_scraped = True
                search_item.save()
            except Exception as e:
                FailedSearchedPosts.objects.create(
                    title=search_item.title,
                    error_text=e.__str__(),
                    searched_new_posts=search_item,
                )
                # TODO: add log
                print(e)
        return search_items

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
                )
            )
            print(i, ':', title)
            print(slug)
        return search_items

    def get_json_and_create_post_by_slug(self, slug):
        print('GET A POST:')
        response = self.send_request(
            settings.POST_JSON_URL_BY_SLUG_TECH_CRUNCH.format(
                slug=slug,
                envelope=settings.ENVELOPE_FALSE,
                embed=settings.EMBED_TRUE,
            )
        )
        if response.status_code == 200:
            post_js = response.json()
            post_js = post_js[0]
            return self.parse_post_json(post_js)
        else:
            raise Exception('status code:', response.status_code)

    def parse_post_json(self, post_js):
        # Get post detail
        id = post_js['id']
        slug = post_js['slug']
        title = post_js['title']['rendered']
        content = post_js['content']['rendered']
        published_date = post_js['date']
        json = post_js
        # Get or create author
        author_js = post_js['_embedded']['author'][0]
        author, _ = Author.objects.get_or_create(
            full_name=author_js['name'],
            twitter_account=author_js['twitter'],
            json=author_js,
            slug=author_js['slug'],
        )
        # Get ot create thumbnail
        thumbnail_url = post_js['_embedded']['wp:featuredmedia'][0]['source_url']
        thumbnail, _ = ImageFile.objects.get_or_create(
            url=thumbnail_url,
            file_name=self.parse_image_name_from_url(thumbnail_url),
            post_id=id,
            is_scraped=False,
        )
        self.get_image_file_from_url(thumbnail_url, thumbnail)
        # Get or create post
        post, created = Post.objects.get_or_create(
            id=id,
            slug=slug,
            title=title,
            content=content,
            published_date=published_date,
            json=json,
            author=author,
            thumbnail=thumbnail,
        )
        if created:
            categories = post_js['categories']
            for i, category_id in enumerate(categories):
                category = Category.objects.get(
                    tech_crunch_id=category_id,
                )
                PostCategory.objects.create(
                    post=post,
                    category=category,
                    category_order=i,
                    title=category.name + ' -> ' + post.title,
                )

        # Get post images
        self.extract_image_from_content(content, post)

        # Add it to constant database table
        scraped_post, created = ScrapedPosts.objects.get_or_create(
            slug=slug,
        )
        print('()'*100)
        print(scraped_post)
        if created:
            categories = post_js['categories']
            print('<>' * 100)
            print(categories)
            for category_id in categories:
                category = Category.objects.get(
                    tech_crunch_id=category_id,
                )
                scraped_post_category, _ = ScrapedPostsCategory.objects.get_or_create(
                    scraped_post=scraped_post,
                    category=category,
                )
        return post

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
