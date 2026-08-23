# search/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from patterns.models import Pattern
from patterns.serializers import PatternListSerializer


class SearchView(APIView):
    """高级搜索"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        keyword = request.GET.get('keyword', '')
        dynasty = request.GET.get('dynasty', '')
        meaning = request.GET.get('meaning', '')
        color = request.GET.get('color', '')
        visual = request.GET.get('visual', '')
        category = request.GET.get('category', '')
        
        queryset = Pattern.objects.filter(status=True)
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(pinyin__icontains=keyword) |
                Q(meaning__icontains=keyword) |
                Q(story__icontains=keyword)
            )
        
        # 朝代筛选
        if dynasty:
            queryset = queryset.filter(dynasty__id=dynasty)
        
        # 分类筛选
        if category:
            queryset = queryset.filter(category__name=category)
        
        # 寓意筛选
        if meaning:
            queryset = queryset.filter(meaning_tags__contains=meaning)
        
        # 色彩筛选
        if color:
            queryset = queryset.filter(color_type=color)
        
        # 视觉特征筛选
        if visual:
            queryset = queryset.filter(visual_type=visual)
        
        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        patterns = queryset[start:end]
        serializer = PatternListSerializer(patterns, many=True)
        
        return Response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })


class SemanticSearchView(APIView):
    """语义搜索（自然语言）"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        text = request.data.get('text', '')
        
        # 简单的关键词匹配
        keywords_map = {
            '婚礼': '喜',
            '春节': '福',
            '生日': '寿',
            '发财': '财',
            '好运': '吉',
            '唐代': 'tang',
            '宋代': 'song',
            '明代': 'ming',
        }
        
        keywords = []
        for key, value in keywords_map.items():
            if key in text:
                keywords.append(value)
        
        if keywords:
            queryset = Pattern.objects.filter(
                Q(meaning_tags__in=keywords) | Q(dynasty__name__in=keywords),
                status=True
            )
        else:
            queryset = Pattern.objects.filter(
                Q(name__icontains=text) | Q(meaning__icontains=text),
                status=True
            )
        
        serializer = PatternListSerializer(queryset[:20], many=True)
        return Response(serializer.data)