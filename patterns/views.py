# patterns/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from .models import Pattern, PatternCategory, Dynasty, UserCollection, UserDesign, UserLike, UserPattern, SystemPattern
from .serializers import (
    PatternListSerializer, PatternDetailSerializer, 
    UserDesignSerializer, PatternCategorySerializer, DynastySerializer, UserPatternSerializer, SystemPatternSerializer
)
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
# patterns/views.py

import os
import uuid
from PIL import Image
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

# 校验上传文件类型
def _is_valid_image_extension(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.png', '.jpg', '.jpeg', '.webp']

# 分析图片适不适合做纹样
def _analyze_image_suitability(image: Image.Image):
    """判断图片是否适合提取纹样"""
    width, height = image.size
    if width < 300 or height < 300:
        return False, '图片尺寸过小，请上传至少 300×300 的图片'

    # 转为灰度图并计算标准差来评估图片对比度
    gray = image.convert('L')
    arr = np.array(gray)
    std = arr.std()
    if std < 12:
        return False, '图片对比度过低，主体不明显，请重新上传边缘更清晰的图片'

    # 背景判断：去掉近白的区域
    mask = arr < 245
    ratio = mask.mean()
    if ratio < 0.03:
        return False, '主体区域过小，无法稳定提取纹样，请上传主体更集中的图片'

    if ratio > 0.85:
        return False, '图片背景过于复杂或画面过满，不适合直接提取纹样，请重新上传'

    return True, 'ok'

# 提取纹样的透明背景
def _extract_pattern_rgba(image: Image.Image):
    """提取透明背景的纹样图像"""
    image = image.convert('RGBA')
    data = np.array(image)

    # 背景部分转透明
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    white_mask = (r > 240) & (g > 240) & (b > 240)
    data[white_mask, 3] = 0  # 将接近白色的部分设为透明

    # 裁剪掉透明区域
    alpha = data[:, :, 3]
    non_empty = np.argwhere(alpha > 0)
    if non_empty.size == 0:
        return None

    y_min, x_min = non_empty.min(axis=0)
    y_max, x_max = non_empty.max(axis=0)

    cropped = data[y_min:y_max + 1, x_min:x_max + 1]
    result = Image.fromarray(cropped, mode='RGBA')
    return result

# 提取纹样的接口
@csrf_exempt
def extract_pattern_view(request):
    """接收图片上传，根据 auto_cutout 决定保存扣图结果或原图"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': '仅支持 POST 请求'
        }, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录后再上传纹样'
        }, status=401)

    uploaded_file = request.FILES.get('image')
    auto_cutout = str(request.POST.get('auto_cutout', 'true')).lower() == 'true'

    if not uploaded_file:
        return JsonResponse({
            'success': False,
            'message': '未接收到上传图片'
        }, status=400)

    if not _is_valid_image_extension(uploaded_file.name):
        return JsonResponse({
            'success': False,
            'message': '仅支持 PNG、JPG、JPEG、WEBP 格式图片'
        }, status=400)

    try:
        image = Image.open(uploaded_file)
        image.load()
    except Exception:
        return JsonResponse({
            'success': False,
            'message': '图片文件无法识别，请重新上传'
        }, status=400)

    try:
        if auto_cutout:
            ok, msg = _analyze_image_suitability(image)
            if not ok:
                return JsonResponse({
                    'success': False,
                    'message': msg
                }, status=400)

            processed_image = _extract_pattern_rgba(image)
            if processed_image is None:
                return JsonResponse({
                    'success': False,
                    'message': '自动扣图失败，请尝试更换背景更干净的图片'
                }, status=400)

            save_meaning = "用户上传的纹样（自动扣图）"
        else:
            processed_image = image.convert('RGBA')
            save_meaning = "用户上传的纹样（原图）"

        save_dir = os.path.join(settings.MEDIA_ROOT, 'user_patterns')
        os.makedirs(save_dir, exist_ok=True)

        uid = uuid.uuid4().hex[:12]
        filename = f'user_pattern_{uid}.png'
        save_path = os.path.join(save_dir, filename)

        processed_image.save(save_path, format='PNG')

        relative_path = f'user_patterns/{filename}'

        create_kwargs = {
            'user': request.user,
            'name': f'用户纹样_{uid[:6]}',
            'meaning': save_meaning,
            'image': relative_path,
        }

        if hasattr(UserPattern, 'auto_cutout'):
            create_kwargs['auto_cutout'] = auto_cutout

        user_pattern = UserPattern.objects.create(**create_kwargs)

        thumbnail_url = f'{settings.MEDIA_URL}{relative_path}'

        return JsonResponse({
            'success': True,
            'id': user_pattern.id,
            'name': user_pattern.name,
            'meaning': user_pattern.meaning,
            'thumbnail': thumbnail_url,
            'auto_cutout': auto_cutout
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'上传处理失败：{str(e)}'
        }, status=500)

class PatternViewSet(viewsets.ReadOnlyModelViewSet):
    """纹样视图集"""
    queryset = Pattern.objects.filter(status=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dynasty', 'category', 'visual_type', 'color_type', 'difficulty']
    search_fields = ['name', 'pinyin', 'meaning', 'story']
    ordering_fields = ['view_count', 'like_count', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatternDetailSerializer
        return PatternListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """获取纹样详情，增加浏览量"""
        instance = self.get_object()
        instance.view_count += 1
        instance.save()

        serializer = self.get_serializer(instance)
        data = serializer.data

        if request.user.is_authenticated:
            data['is_liked'] = UserLike.objects.filter(user=request.user, pattern=instance).exists()
            data['is_collected'] = UserCollection.objects.filter(user=request.user, pattern=instance).exists()
        else:
            data['is_liked'] = False
            data['is_collected'] = False

        return Response(data)
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """随机获取纹样"""
        count = int(request.GET.get('count', 10))
        patterns = Pattern.objects.filter(status=True).order_by('?')[:count]
        serializer = PatternListSerializer(patterns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """推荐纹样"""
        patterns = Pattern.objects.filter(is_recommended=True, status=True)[:12]
        serializer = PatternListSerializer(patterns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot(self, request):
        """热门纹样"""
        patterns = Pattern.objects.filter(is_hot=True, status=True)[:12]
        serializer = PatternListSerializer(patterns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """点赞/取消点赞"""
        pattern = self.get_object()
        user = request.user

        obj, created = UserLike.objects.get_or_create(
            user=user,
            pattern=pattern
        )

        if created:
            pattern.like_count += 1
            pattern.save()
            return Response({
                'liked': True,
                'like_count': pattern.like_count,
                'message': '点赞成功'
            })

        obj.delete()
        pattern.like_count = max(pattern.like_count - 1, 0)
        pattern.save()
        return Response({
            'liked': False,
            'like_count': pattern.like_count,
            'message': '已取消点赞'
        })


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def collect(self, request, pk=None):
        """收藏/取消收藏"""
        pattern = self.get_object()
        user = request.user

        obj, created = UserCollection.objects.get_or_create(
            user=user,
            pattern=pattern
        )

        if created:
            pattern.collect_count += 1
            pattern.save()
            return Response({
                'collected': True,
                'collect_count': pattern.collect_count,
                'message': '收藏成功'
            })

        obj.delete()
        pattern.collect_count = max(pattern.collect_count - 1, 0)
        pattern.save()
        return Response({
            'collected': False,
            'collect_count': pattern.collect_count,
            'message': '已取消收藏'
        })
    
    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """时间轴展示纹样演变"""
        timeline_data = []
        dynasties = Dynasty.objects.all().order_by('start_year')
        
        for dynasty in dynasties:
            patterns = Pattern.objects.filter(dynasty=dynasty, status=True)[:5]
            timeline_data.append({
                'dynasty': dynasty.name,
                'patterns': PatternListSerializer(patterns, many=True).data
            })
        return Response(timeline_data)


class DesignViewSet(viewsets.ModelViewSet):
    """设计作品视图集"""
    serializer_class = UserDesignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'public':
            return UserDesign.objects.filter(is_public=True).select_related('user', 'pattern')
        return UserDesign.objects.filter(user=self.request.user).select_related('user', 'pattern')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """公开作品展示"""
        designs = UserDesign.objects.filter(is_public=True).select_related('user', 'pattern')[:20]
        serializer = self.get_serializer(designs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        """我的作品"""
        designs = UserDesign.objects.filter(user=request.user).select_related('user', 'pattern')
        serializer = self.get_serializer(designs, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """分类视图集"""
    queryset = PatternCategory.objects.all()
    serializer_class = PatternCategorySerializer
    permission_classes = [AllowAny]



class DynastyViewSet(viewsets.ReadOnlyModelViewSet):
    """朝代视图集"""
    queryset = Dynasty.objects.all().order_by('start_year')
    serializer_class = DynastySerializer
    permission_classes = [AllowAny]


# 前端页面视图
class IndexView(TemplateView):
    """首页"""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 获取推荐纹样和热门纹样
        context['recommended_patterns'] = Pattern.objects.filter(is_recommended=True, status=True)[:8]
        context['hot_patterns'] = Pattern.objects.filter(is_hot=True, status=True)[:8]
        return context


class DesignView(TemplateView):
    """设计页面"""
    template_name = 'design.html'


class PatternDetailView(DetailView):
    """纹样详情页"""
    model = Pattern
    template_name = 'pattern-detail.html'
    context_object_name = 'pattern'
    pk_url_kwarg = 'pk'


class MyCollectionsView(TemplateView):
    """我的收藏页面"""
    template_name = 'my_collections.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['collections'] = self.request.user.collections.all()
        return context


class MyDesignsView(TemplateView):
    """我的设计页面"""
    template_name = 'my_designs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['designs'] = self.request.user.designs.all()
        return context

@api_view(['GET'])
@permission_classes([AllowAny])
def get_stats(request):
    """获取统计数据"""
    from django.db.models import Count
    
    pattern_count = Pattern.objects.filter(status=True).count()
    design_count = UserDesign.objects.filter(is_public=True).count()
    dynasty_count = Dynasty.objects.exclude(name__in=['不明']).count()
    
    return Response({
        'pattern_count': pattern_count,
        'design_count': design_count,
        'dynasty_count': dynasty_count,
    })

class SystemPatternListView(generics.ListAPIView):
    """获取系统推荐的纹样"""
    queryset = SystemPattern.objects.all().order_by('created_at')  # 添加排序
    serializer_class = SystemPatternSerializer

class UserPatternListView(generics.ListCreateAPIView):
    serializer_class = UserPatternSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        print(f"=== 调试 UserPatternListView ===")
        print(f"request.user: {self.request.user}")
        print(f"request.user.id: {self.request.user.id}")
        print(f"request.user.is_authenticated: {self.request.user.is_authenticated}")
        
        queryset = UserPattern.objects.filter(user=self.request.user).order_by('-created_at')
        print(f"查询到的数量: {queryset.count()}")
        
        return queryset

class UserPatternDetailView(APIView):
    """单个用户纹样的获取、更新、删除"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk, user):
        return get_object_or_404(UserPattern, pk=pk, user=user)
    
    def get(self, request, pk):
        """获取单个纹样详情"""
        pattern = self.get_object(pk, request.user)
        serializer = UserPatternSerializer(pattern)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """更新纹样（重命名等）"""
        pattern = self.get_object(pk, request.user)
        serializer = UserPatternSerializer(pattern, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        """删除纹样"""
        pattern = self.get_object(pk, request.user)
        # 删除文件
        if pattern.image and os.path.isfile(pattern.image.path):
            os.remove(pattern.image.path)
        pattern.delete()
        return Response(status=204)