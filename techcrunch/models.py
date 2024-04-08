from django.db import models
from abc import abstractmethod

from django.conf import settings
from django.utils.html import mark_safe
from bs4 import BeautifulSoup


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
    json = models.JSONField(default=dict, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.full_name


class Category(BaseModel):
    slug = models.SlugField(null=False, unique=True)
    name = models.CharField(null=True, blank=True, max_length=128)
    tech_crunch_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    json = models.JSONField(default=dict)

    def local_post_count(self):
        return len(PostCategory.objects.filter(category=self))

    def online_post_count(self):
        return self.json['count']

    def __str__(self):
        return self.slug


class ImageFile(BaseModel):
    url = models.URLField(null=False)
    file_name = models.CharField(max_length=255, null=False, blank=False)
    local_path = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/')
    post_id = models.IntegerField(default=0)
    is_scraped = models.BooleanField(default=False)

    def img_preview(self):
        try:
            return mark_safe(f'<img src = "{self.image.url}" style="max-width:200px; max-height:200px"/>')
        except Exception as e:
            return e.__str__()

    def __str__(self):
        return self.file_name


class Post(BaseModel):
    id = models.IntegerField(null=False, blank=False, primary_key=True)
    slug = models.SlugField(null=False, unique=True)
    title = models.CharField(null=False, blank=False, max_length=255)
    content = models.TextField(null=True, blank=True)
    published_date = models.DateTimeField()
    json = models.JSONField(default=dict)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
        blank=True,
    )
    thumbnail = models.ForeignKey(
        ImageFile,
        on_delete=models.PROTECT,
        related_name="posts_thumbnail",
        null=True,
        blank=True,
    )

    def img_preview(self):  # new
        return mark_safe(f'<img src = "{self.thumbnail.image.url}" style="max-width:200px; max-height:200px"/>')

    def get_raw_text(self):
        soup = BeautifulSoup(self.content, "html.parser")
        return soup.text

    def __str__(self):
        return self.title


class ImagePost(BaseModel):
    image_order = models.IntegerField(default=0)
    title = models.CharField(max_length=127)
    post = models.ForeignKey(
        Post, on_delete=models.PROTECT, related_name="images"
    )
    image = models.ForeignKey(
        ImageFile, on_delete=models.CASCADE, related_name="posts"
    )

    def __str__(self):
        return self.post.title + " - " + self.image.file_name


class PostCategory(BaseModel):
    category_order = models.IntegerField(default=0)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return (
            self.category.name
            + " - "
            + self.post.title[0:settings.BRIEF_CHAR_COUNT_TITLE]
        )


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
        SearchedKeyword, on_delete=models.CASCADE, related_name="searched_post_by_keyword",
    )
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, related_name="searched_post_by_keyword", null=True,
    )

    def __str__(self):
        return self.title


class DailySearch(BaseModel):
    is_complete = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="daily_search"
    )
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.category.name + " - " + self.created_at


class PostDailySearch(BaseModel):
    daily_search = models.ForeignKey(
        DailySearch, on_delete=models.PROTECT, related_name="posts",
    )
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, related_name="category_new_posts", null=True,
    )

    def __str__(self):
        return self.post.title


class FailedCategoryNewPosts(BaseModel):
    title = models.CharField(max_length=127)
    error_text = models.TextField(blank=True)
    daily_search = models.ForeignKey(
        DailySearch, on_delete=models.CASCADE, related_name="failed_posts",
    )

    def __str__(self):
        return self.title


class FailedSearchedPosts(BaseModel):
    title = models.CharField(max_length=127)
    error_text = models.TextField(blank=True)
    searched_new_posts = models.ForeignKey(
        SearchedPostByKeyword, on_delete=models.PROTECT, related_name="failed_posts",
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
