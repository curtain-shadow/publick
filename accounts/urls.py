# accounts/urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

urlpatterns = [
    # 为每个 API 路由添加 csrf_exempt 豁免
    path('login/', csrf_exempt(views.login_view), name='api_login'),
    path('register/', csrf_exempt(views.api_register_view), name='api_register'),
    path('check-user/', csrf_exempt(views.check_user_view), name='check-user'),
    path('send-verification-code/', csrf_exempt(views.send_verification_code), name='send-verification-code'),
    path('reset-password-with-code/', csrf_exempt(views.reset_password_with_code), name='reset-password-with-code'),
]