# design/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patterns.views import DesignViewSet

router = DefaultRouter()
router.register(r'works', DesignViewSet, basename='design')

urlpatterns = [
    path('', include(router.urls)),
]