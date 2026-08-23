# chinese_pattern_library/views.py
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

class IndexView(TemplateView):
    template_name = 'index.html'

class DesignView(TemplateView):
    template_name = 'design.html'

class PatternDetailView(TemplateView):
    template_name = 'pattern-detail.html'

class MyCollectionsView(TemplateView):
    template_name = 'my-collections.html'

class DynastyTimeView(TemplateView):
    template_name = 'dynasty-time.html'

@ensure_csrf_cookie
def get_user_status(request):
    """获取当前用户登录状态"""
    if request.user.is_authenticated:
        return JsonResponse({
            'is_authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
        })
    return JsonResponse({
        'is_authenticated': False,
    })