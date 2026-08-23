# chinese_pattern_library/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import register_view
from patterns import views
from . import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register_view, name='register'), 
    path('api/patterns/', include('patterns.urls')),
    path("community/", include("community.urls")),
    path("api/community/", include("community.api_urls")),
    path('api/search/', include('search.urls')),
    
    path('api/user/status/', main_views.get_user_status, name='user_status'),
    path('api/patterns/extract/', views.extract_pattern_view, name='extract_pattern'),  # 上传并提取纹样
    # 前端页面路由
    path('', views.IndexView.as_view(), name='index'),
    path('design/', views.DesignView.as_view(), name='design'),
    path('pattern/<int:pk>/', views.PatternDetailView.as_view(), name='pattern-detail'),
    path('dynasty-time/', main_views.DynastyTimeView.as_view(), name='dynasty-time'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)