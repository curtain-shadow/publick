# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    """用户注册表单"""
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码（至少8位）'
        }),
        min_length=8,
        error_messages={
            'min_length': '密码长度不能少于8位',
            'required': '密码不能为空',
        }
    )
    
    password_confirm = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入密码'
        }),
        error_messages={
            'required': '请再次输入密码',
        }
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱地址'
            }),
        }
        labels = {
            'username': '用户名',
            'email': '邮箱',
        }
        error_messages = {
            'username': {
                'required': '用户名不能为空',
                'max_length': '用户名长度不能超过150个字符',
            },
            'email': {
                'required': '邮箱不能为空',
                'invalid': '请输入有效的邮箱地址',
            },
        }
    
    def clean_username(self):
        """验证用户名唯一性"""
        username = self.cleaned_data.get('username')
        if not username:
            return username
        
        if User.objects.filter(username=username).exists():
            raise ValidationError('该用户名已被使用，请换一个')
        
        # 检查用户名是否包含非法字符
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            raise ValidationError('用户名只能包含字母、数字、下划线和中文字符')
        
        return username
    
    def clean_email(self):
        """验证邮箱唯一性和格式"""
        email = self.cleaned_data.get('email')
        if not email:
            return email
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')
        
        # 更详细的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('请输入有效的邮箱地址')
        
        return email
    
    def clean(self):
        """验证两次密码是否一致"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # 只在两个字段都有值时才进行比对
        if password and password_confirm:
            if password != password_confirm:
                # 添加字段级别的错误，这样错误会显示在确认密码字段旁边
                self.add_error('password_confirm', '两次输入的密码不一致，请重新输入')
        
        return cleaned_data
    
    def save(self, commit=True):
        """保存用户，确保密码被正确加密"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user