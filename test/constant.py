import requests

DEFAULT_SEARCH_PAGE_COUNT_TECH_CRUNCH = 5
DEFAULT_POST_COUNT_TECH_CRUNCH = 20

# ---URLS---
# BASE URLS
BASE_URL = 'https://www.techcrunch.com'
WP_JSON_BASE_URL = BASE_URL + '/wp-json'


# ***SEARCH***
SEARCH_URL_TECH_CRUNCH = (
    'https://search.techcrunch.com/search?p={keyword}&b={page}1'
)


# ***CATEGORY***
# envelope: get Meta data about this json | (true/false)
ALL_CATEGORIES_JSON_URL_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp/v2/categories?per_page={count}&_envelope={envelope}'
)
CATEGORY_JSON_URL_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp/v2/categories/{id}'
)


# ***POST***
# envelope: get Meta data about this json | (true/false)
# embed: get all data about author and category in "_embedded" tag | (true/false)
POST_JSON_URL_BY_SLUG_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp/v2/posts?slug={slug}&_embed={embed}&_envelope={envelope}'
)
POST_JSON_URL_BY_ID_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp-json/wp/v2/posts/{id}?_embed={embed}&_envelope={envelope}'
)


# ***USER***
USER_JSON_URL_BY_SLUG_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp-json/tc/v1/users?slug={slug}'
)
USER_JSON_URL_BY_ID_TECH_CRUNCH = (
    WP_JSON_BASE_URL + '/wp-json/tc/v1/users/{id}'
)
