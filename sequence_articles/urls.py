from django.urls import path
from .views import HomePageView,category_detail,article_detail,search_articles

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path("category/<slug:slug>/", category_detail, name="category_detail"),
    path("article/<slug:slug>/", article_detail, name="article_detail"),
    path('search/', search_articles, name='search'),



]
