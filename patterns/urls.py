# patterns/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patterns', views.PatternViewSet, basename='pattern')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'dynasties', views.DynastyViewSet, basename='dynasty')

urlpatterns = [
    path('', include(router.urls)),
     path('stats/', views.get_stats, name='stats'),  # 统计接口
     path('extract/', views.extract_pattern_view, name='extract_pattern'),
     path('user-patterns/', views.UserPatternListView.as_view(), name='user_pattern_list'),
     path('user-patterns/<int:pk>/', views.UserPatternDetailView.as_view(), name='user_pattern_detail'),
     path('system-patterns/', views.SystemPatternListView.as_view(), name='system_patterns_list'),  # 系统推荐纹样
     
]