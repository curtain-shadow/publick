# patterns/serializers.py
from rest_framework import serializers
from .models import (
    Pattern, PatternCategory, Dynasty, PatternImage, 
    PatternColor, UserDesign, UserCollection, UserPattern, SystemPattern
)

class DynastySerializer(serializers.ModelSerializer):
    """朝代序列化器"""
    class Meta:
        model = Dynasty
        fields = ['id', 'name', 'start_year', 'end_year', 'order']

class PatternCategorySerializer(serializers.ModelSerializer):
    """纹样分类序列化器"""
    class Meta:
        model = PatternCategory
        fields = ['id', 'name', 'icon', 'description', 'parent']

class PatternImageSerializer(serializers.ModelSerializer):
    """纹样图片序列化器"""
    class Meta:
        model = PatternImage
        fields = ['id', 'image', 'is_main', 'description', 'order']

class PatternColorSerializer(serializers.ModelSerializer):
    """纹样配色序列化器"""
    class Meta:
        model = PatternColor
        fields = ['id', 'name', 'color_code', 'ratio']

class PatternListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    dynasty_name = serializers.CharField(source='dynasty.name', read_only=True)
    
    class Meta:
        model = Pattern
        fields = [
            'id', 'name', 'thumbnail', 'meaning', 'dynasty_name', 
            'category_name', 'view_count', 'like_count', 'difficulty',  # 添加 view_count
            'visual_type', 'color_type'
        ]

class PatternDetailSerializer(serializers.ModelSerializer):
    """纹样详情序列化器"""
    images = PatternImageSerializer(many=True, read_only=True)
    colors = PatternColorSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    dynasty_name = serializers.CharField(source='dynasty.name', read_only=True)
    
    class Meta:
        model = Pattern
        fields = '__all__'

class UserDesignSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    pattern_name = serializers.CharField(source='pattern.name', read_only=True)
    pattern_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    pattern = PatternListSerializer(read_only=True)

    class Meta:
        model = UserDesign
        fields = [
            'id',
            'name',
            'username',
            'pattern',
            'pattern_name',
            'pattern_id',
            'thumbnail',
            'design_data',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'username', 'pattern_name', 'created_at', 'updated_at']

    def create(self, validated_data):
        pattern_id = validated_data.pop('pattern_id', None)
        if pattern_id:
            validated_data['pattern_id'] = pattern_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        pattern_id = validated_data.pop('pattern_id', None)
        if pattern_id is not None:
            instance.pattern_id = pattern_id
        return super().update(instance, validated_data)
        
class UserCollectionSerializer(serializers.ModelSerializer):
    """用户收藏序列化器"""
    pattern_info = PatternListSerializer(source='pattern', read_only=True)
    
    class Meta:
        model = UserCollection
        fields = ['id', 'pattern', 'pattern_info', 'created_at']

class UserPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPattern
        fields = ['id', 'name', 'meaning', 'image']

class SystemPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPattern
        fields = ['id', 'name', 'meaning', 'image']  # 系统推荐的纹样字段