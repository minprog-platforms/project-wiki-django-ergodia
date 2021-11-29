from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry_name>", views.entry_pages, name="entry_page"),
    path("search", views.search_pages, name="search_pages"),
    path("error", views.error_page, name="error_page"),
    path("add_page", views.add_page, name="add_page"),
    path("wiki/<str:entry_name>/edit", views.edit_page, name="edit_page"),
    path("random", views.random_page, name="random_page")
]
