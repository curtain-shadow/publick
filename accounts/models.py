# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('个人简介', blank=True, max_length=500)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)
    
    def __str__(self):
        return self.user.username

class VerificationCode(models.Model):
    """验证码表"""
    email = models.EmailField('邮箱')
    code = models.CharField('验证码', max_length=6)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_used = models.BooleanField('是否已使用', default=False)
    
    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} - {self.code}"
    
    def is_expired(self):
        """检查验证码是否过期"""
        from django.utils import timezone
        from django.conf import settings
        expire_seconds = getattr(settings, 'VERIFICATION_CODE_TIMEOUT', 300)
        delta = timezone.now() - self.created_at
        return delta.total_seconds() > expire_seconds