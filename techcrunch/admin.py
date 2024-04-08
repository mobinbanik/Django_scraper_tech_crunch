from django.contrib import admin
from django.contrib.admin import register
from import_export.admin import ImportExportModelAdmin
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
    PostDailySearch,
    FailedCategoryNewPosts,
    FailedSearchedPosts,
    ScrapedPosts,
    ScrapedPostsCategory,

)


# Register your models here.
class BaseAdmin(admin.ModelAdmin):
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
        'tech_crunch_id',
        'name',
        'description',
        'local_post_count',
        'online_post_count',
        'updated_at'
    )
    search_fields = (
        'name',
        'description',
    )


@register(Post)
class PostAdmin(BaseAdmin, ImportExportModelAdmin):
    list_display = (
        'img_preview',
        'title',
        'author',
        'published_date',
        'slug',
        'is_active',
    )
    list_filter = (
        'published_date',
        'author'
    )
    search_fields = (
        'author',
        'title',
        'content',
    )


@register(PostCategory)
class PostCategoryAdmin(BaseAdmin, ImportExportModelAdmin):
    list_display = (
        'title',
        'category_order',
    )
    list_filter = (
        'category',
    )
    search_fields = (
        'category_name',
        'post_title',
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


@register(ImageFile)
class ImageFileAdmin(BaseAdmin, ImportExportModelAdmin):
    list_display = (
        'img_preview',
        'file_name',
        'post_id',
    )


@register(ImagePost)
class ImagePostAdmin(BaseAdmin, ImportExportModelAdmin):
    list_display = (
        'post_id',
        'title',
        'image_order',
    )
    search_fields = (
        'post_title',
    )


@register(DailySearch)
class DailySearchAdmin(BaseAdmin):
    list_display = (
        'is_complete',
        'created_at',
    )
    list_filter = (
        'is_complete',
    )
    search_fields = (
        'category__name',
    )


@register(PostDailySearch)
class PostDailySearchAdmin(BaseAdmin):
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


@register(FailedSearchedPosts)
class FailedSearchedPostsAdmin(BaseAdmin):
    list_display = (
        'title',
        'error_text',
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
    list_display = (
        'scraped_post',
        'category',
        'created_at',
    )

    list_filter = (
        'category__name',
    )
    search_fields = (
        'category__name',
        'scraped_post__slug',
    )

