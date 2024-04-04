from tkinter import Image

from django.db import models
from abc import abstractmethod

from django.conf import settings


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError('Implement __str__ method')

    class Meta:
        abstract = True


class Author(BaseModel):
    full_name = models.CharField(max_length=128, null=False, blank=False)
    twitter_account = models.CharField(max_length=255)
    json = models.JSONField(default=dict,)

    def __str__(self):
        return self.full_name


class Category(BaseModel):
    slug = models.SlugField(null=False, unique=True)
    name = models.CharField(null=False, blank=False, max_length=128)
    tech_crunch_id = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    post_count = models.IntegerField(null=False, blank=False, default=0)
    json = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class ImageFile(BaseModel):
    url = models.URLField(null=False)
    file_name = models.CharField(max_length=255, null=False, blank=False)
    local_path = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.file_name


class Post(BaseModel):
    slug = models.SlugField(null=False, unique=True)
    title = models.CharField(null=False, blank=False, max_length=255)
    content = models.TextField(null=True, blank=True)
    published_date = models.DateTimeField()
    json = models.JSONField(default=dict)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="posts",
    )
    thumbnail = models.ForeignKey(
        ImageFile, on_delete=models.PROTECT, related_name="posts"
    )

    def __str__(self):
        return self.title

    @property
    def raw_content(self):
        # probably delete content and get it from json
        return self.content


class Keyword(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.title


class SearchedKeyword(BaseModel):
    page_count = models.IntegerField(null=False, blank=False, default=3)
    keyword = models.ForeignKey(
        Keyword, on_delete=models.CASCADE, related_name="searched_keyword",
    )

    def __str__(self):
        return self.keyword.title


class SearchedPostByKeyword(BaseModel):
    title = models.CharField(max_length=255, null=False, blank=False)
    post_slug = models.SlugField(null=False, unique=False)
    is_scraped = models.BooleanField(default=False)
    url = models.URLField(null=False, blank=False, max_length=500)
    searched_by_keyword = models.ForeignKey(
        SearchedKeyword, on_delete=models.CASCADE, related_name="posts",
    )
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, related_name="searched_keywords",
    )

    def __str__(self):
        return self.title


class PostCategory(BaseModel):
    category_order = models.IntegerField(default=0)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )

    def __str__(self):
        return (
            self.category.name
            + " - "
            + self.post.title[0:settings.BRIEF_CHAR_COUNT_TITLE]
        )


class PostImage(BaseModel):
    image_order = models.IntegerField(default=0)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ForeignKey(
        ImageFile, on_delete=models.CASCADE, related_name="posts"
    )

    def __str__(self):
        return self.post.title + " - " + self.image.file_name


class DailySearch(BaseModel):
    new_post_count = models.IntegerField(default=20)
    scraped_post_count = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="daily_search"
    )

    def __str__(self):
        return self.category.name + " - " + self.new_post_count


class CategoryNewPosts(BaseModel):
    title = models.CharField(max_length=127)
    is_scraped = models.BooleanField(default=False)
    json_envelope_header = models.JSONField(default=dict)
    daily_search = models.ForeignKey(
        DailySearch, on_delete=models.CASCADE, related_name="posts",
    )

    def __str__(self):
        return self.title


class PostCategoryNewPost(BaseModel):
    is_scraped = models.BooleanField(default=False)
    post_url = models.URLField()
    category_new_posts = models.ForeignKey(
        CategoryNewPosts, on_delete=models.PROTECT, related_name="posts"
    )
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, related_name="category_new_posts",
    )

    def __str__(self):
        return self.post.title


class FailedCategoryNewPosts(BaseModel):
    title = models.CharField(max_length=127)
    error_text = models.TextField(blank=True)
    category_new_posts = models.ForeignKey(
        CategoryNewPosts, on_delete=models.CASCADE, related_name="faild_posts",
    )

    def __str__(self):
        return self.title


class ScrapedPosts(BaseModel):
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.slug


class ScrapedPostsCategory(BaseModel):
    scraped_posts = models.ForeignKey(
        ScrapedPosts, on_delete=models.CASCADE, related_name="category"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="scraped_posts"
    )

    def __str__(self):
        return self.category.name + " - " + self.scraped_posts.slug
