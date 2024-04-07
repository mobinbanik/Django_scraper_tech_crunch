from django.contrib import admin
from django.contrib.admin import register
from .models import (
    Author,
    Category,
    ImageFile,
    Post,
    Keyword,
    SearchedKeyword,
    SearchedPostByKeyword,
    PostCategory,
    ImagePost,
    DailySearch,
    CategoryNewPosts,
    PostCategoryNewPost,
    FailedCategoryNewPosts,
    ScrapedPosts,
    ScrapedPostsCategory,
)


# Register your models here.
class BaseAdmin(admin.ModelAdmin):
    # list_display = (
    #     'is_active',
    # )
    actions = ['activate', 'deactivate']

    @admin.action
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


@register(Author)
class AuthorAdmin(BaseAdmin):
    list_display = (
        'full_name',
        'is_active',
    )
    search_fields = (
        'full_name',
    )


@register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = (
        'name',
        'post_count',
    )
    search_fields = (
        'name',
        'post_count',
        'description',
    )


@register(ImageFile)
class ImageFileAdmin(BaseAdmin):
    list_display = (
        'file_name',
    )


@register(Post)
class PostAdmin(BaseAdmin):
    list_display = (
        'slug',
        'author',
        'title',
        'published_date',
    )
    list_filter = (
        'published_date',
        'author'
    )
    search_fields = (
        'author',
        'title',
        'content'
    )


@register(Keyword)
class KeywordAdmin(BaseAdmin):
    list_display = (
        'title',
    )
    search_fields = (
        'title',
    )


@register(SearchedKeyword)
class SearchedKeywordAdmin(BaseAdmin):
    list_display = (
        'page_count',
    )
    search_fields = (
        'keyword__title',
    )


@register(SearchedPostByKeyword)
class SearchedPostByKeywordAdmin(BaseAdmin):
    list_display = (
        'title',
        'is_scraped',
        'post_slug',
    )
    list_filter = (
        'is_scraped',
    )
    search_fields = (
        'post_slug',
        'title',
    )


@register(PostCategory)
class PostCategoryAdmin(BaseAdmin):
    list_display = (
        'category_order',
    )
    list_filter = (
        'category',
    )
    search_fields = (
        'category_name',
        'post_title',
    )


@register(ImagePost)
class ImagePostAdmin(BaseAdmin):
    list_display = (
        'image_order',
    )
    search_fields = (
        'post_title',
    )


@register(DailySearch)
class DailySearchAdmin(BaseAdmin):
    list_display = (
        'new_post_count',
        'scraped_post_count',
    )
    list_filter = (
        'is_complete',
    )
    search_fields = (
        'category__name',
    )


@register(CategoryNewPosts)
class CategoryNewPostsAdmin(BaseAdmin):
    list_display = (
        'title',
        'is_scraped',
    )
    list_filter = (
        'is_scraped',
    )
    search_fields = (
        'daily_search__category__name',
    )


@register(PostCategoryNewPost)
class PostCategoryNewPostAdmin(BaseAdmin):
    search_fields = (
        'post__title',
    )


@register(FailedCategoryNewPosts)
class FailedCategoryNewPostsAdmin(BaseAdmin):
    list_display = (
        'title',
        'error_text',
    )
    search_fields = (
        'category_new_posts__title',
        'category_new_posts__daily_search__category__name',
    )


@register(ScrapedPosts)
class ScrapedPostsAdmin(BaseAdmin):
    list_display = (
        'slug',
        'created_at',
    )
    search_fields = (
        'slug',
    )


@register(ScrapedPostsCategory)
class ScrapedPostsCategoryAdmin(BaseAdmin):
    list_filter = (
        'category__name',
    )
    search_fields = (
        'category__name',
        'scraped_posts__slug',
    )

