# accounts/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    自定义认证后端：支持用户名或邮箱登录
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写 authenticate 方法，支持通过用户名或邮箱认证
        """
        if username is None or password is None:
            return None
        
        try:
            # 尝试通过用户名或邮箱查找用户
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            # 如果用户不存在，运行默认的认证器（避免时序攻击）
            User().set_password(password)
            return None
        
        # 验证密码
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None