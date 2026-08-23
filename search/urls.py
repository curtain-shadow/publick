# search/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('semantic/', views.SemanticSearchView.as_view(), name='semantic_search'),
]