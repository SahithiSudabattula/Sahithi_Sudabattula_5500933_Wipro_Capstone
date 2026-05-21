from pages.login_page import LoginPage
from pages.search_page import SearchPage


def get_login_page(context):
    login_page = getattr(context, "login_page", None)
    if login_page is None:
        login_page = LoginPage(getattr(context, "driver"))
        setattr(context, "login_page", login_page)
    return login_page


def get_search_page(context):
    search_page = getattr(context, "search_page", None)
    if search_page is None:
        search_page = SearchPage(getattr(context, "driver"))
        setattr(context, "search_page", search_page)
    return search_page
