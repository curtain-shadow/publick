from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """为API路由禁用CSRF检查"""
    
    def process_request(self, request):
        # 豁免所有以 /api/auth/ 开头的路由
        if request.path.startswith('/api/auth/'):
            setattr(request, '_dont_enforce_csrf_checks', True)