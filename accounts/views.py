# accounts/views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods  # 添加这行
from django.http import JsonResponse  # 添加这行
import json  # 添加这行
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import UserRegistrationForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string
from .models import VerificationCode
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

# ========== API 视图 ==========
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    """API: 用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"登录尝试: username={username}")
    
    if not username or not password:
        return Response({
            'error': '请填写用户名和密码',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)  # 现在 login 已经导入了
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })
    else:
        return Response({
            'success': False,
            'error': '用户名或密码错误'
        }, status=status.HTTP_401_UNAUTHORIZED)
        
# ========== 网页视图 ==========

def register_view(request):
    """网页: 用户注册（用于浏览器访问）"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # 注册后自动登录 - 直接调用 auth_login 并设置 backend
            from django.conf import settings
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            auth_login(request, user)
            
            messages.success(request, f'欢迎 {user.username}！注册成功！')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def generate_verification_code():
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))

@csrf_exempt
@api_view(['POST'])
def api_register_view(request):
    """API: 用户注册（供前端AJAX调用）"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({'error': '请填写用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def check_user_view(request):
    """验证用户名和邮箱是否匹配"""
    username = request.data.get('username')
    email = request.data.get('email')
    
    if not username or not email:
        return Response({'error': '请填写完整信息'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username, email=email)
        return Response({'success': True, 'message': '验证通过'})
    except User.DoesNotExist:
        return Response({'error': '用户名与邮箱不匹配'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])  # 改成 @api_view 保持风格一致
def send_verification_code(request):
    """发送验证码"""
    email = request.data.get('email')  # 直接使用 request.data，不需要 json.loads
    
    if not email:
        return Response({'error': '请填写邮箱地址'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查邮箱是否存在
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': '该邮箱未注册'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 生成验证码
    code = generate_verification_code()
    
    # 保存验证码到数据库
    VerificationCode.objects.create(email=email, code=code)
    
    # 准备邮件内容
    subject = '密码重置验证码 - 中华传统纹样数字库'
    
    # 创建HTML内容
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>验证码</title>
        <style>
            body {{ font-family: 'Microsoft YaHei', sans-serif; background-color: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); padding: 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; font-size: 24px; }}
            .content {{ padding: 30px; text-align: center; }}
            .code {{ font-size: 32px; font-weight: bold; color: #8B4513; letter-spacing: 5px; margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 10px; }}
            .message {{ color: #666; line-height: 1.6; }}
            .warning {{ font-size: 12px; color: #999; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }}
            .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>中华传统纹样数字库</h1>
            </div>
            <div class="content">
                <div class="message">您好，{user.username}！</div>
                <div class="message">您正在重置密码，验证码为：</div>
                <div class="code">{code}</div>
                <div class="message">验证码有效期为5分钟，请尽快使用。</div>
                <div class="warning">如果您没有申请重置密码，请忽略此邮件。</div>
            </div>
            <div class="footer">
                &copy; 2024 中华传统纹样数字库 | 传承文化之美
            </div>
        </div>
    </body>
    </html>
    '''
    
    # 纯文本版本（作为备用）
    plain_message = f'您好 {user.username}！\n\n您正在重置密码，验证码为：{code}\n\n验证码有效期为5分钟，请尽快使用。\n\n如果您没有申请重置密码，请忽略此邮件。'
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({  # 改成 Response 保持风格一致
            'success': True,
            'message': '验证码已发送到您的邮箱',
            'email': email
        })
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return Response({'error': f'邮件发送失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@csrf_exempt
@api_view(['POST'])
def reset_password_with_code(request):
    """使用验证码重置密码"""
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    # 验证输入
    if not all([email, code, new_password]):
        return Response({'error': '请填写完整信息'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 6:
        return Response({'error': '密码长度不能少于6位'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 验证邮箱是否存在
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': '邮箱不存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 查找最新的未使用的验证码
    try:
        vc = VerificationCode.objects.filter(
            email=email, 
            code=code, 
            is_used=False
        ).latest('created_at')
    except VerificationCode.DoesNotExist:
        return Response({'error': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查是否过期
    if vc.is_expired():
        return Response({'error': '验证码已过期，请重新获取'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 标记验证码为已使用
    vc.is_used = True
    vc.save()
    
    # 重置密码
    user.set_password(new_password)
    user.save()
    
    # 删除旧的token
    Token.objects.filter(user=user).delete()
    
    return Response({'message': '密码重置成功！'})