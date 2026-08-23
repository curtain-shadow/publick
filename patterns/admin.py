# patterns/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Count
from .models import Pattern, PatternCategory, Dynasty, PatternImage, PatternColor, UserDesign

@admin.register(Dynasty)
class DynastyAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_year', 'end_year', 'order', 'pattern_count']
    list_editable = ['order']
    list_per_page = 20
    
    def pattern_count(self, obj):
        count = obj.pattern_set.filter(status=True).count()
        if count > 0:
            url = reverse('admin:patterns_pattern_changelist') + f'?dynasty__id__exact={obj.id}'
            return format_html('<a href="{}" style="font-weight: bold;">{} 个纹样</a>', url, count)
        return '0 个纹样'
    pattern_count.short_description = '纹样数量'

@admin.register(PatternCategory)
class PatternCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'parent', 'pattern_count']
    list_filter = ['parent']
    search_fields = ['name']
    list_per_page = 30
    
    def pattern_count(self, obj):
        count = obj.pattern_set.filter(status=True).count()
        if count > 0:
            url = reverse('admin:patterns_pattern_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}" style="font-weight: bold;">{} 个纹样</a>', url, count)
        return '0 个纹样'
    pattern_count.short_description = '纹样数量'
    
    fieldsets = (
        ('分类信息', {
            'fields': ('name', 'parent', 'icon')
        }),
        ('详细描述', {
            'fields': ('description',),
        }),
    )
    
    actions = ['make_top_level', 'delete_empty_categories']
    
    def make_top_level(self, request, queryset):
        updated = queryset.update(parent=None)
        self.message_user(request, f'已将 {updated} 个分类转为顶级分类')
    make_top_level.short_description = '转为顶级分类'
    
    def delete_empty_categories(self, request, queryset):
        deleted_count = 0
        for category in queryset:
            if category.pattern_set.count() == 0:
                category.delete()
                deleted_count += 1
        self.message_user(request, f'已删除 {deleted_count} 个空分类')
    delete_empty_categories.short_description = '删除空分类'

class PatternImageInline(admin.TabularInline):
    model = PatternImage
    extra = 1
    fields = ['image', 'is_main', 'description', 'order']
    show_change_link = True

class PatternColorInline(admin.TabularInline):
    model = PatternColor
    extra = 3
    fields = ['name', 'color_code', 'ratio']

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    # 完善列表显示字段
    list_display = [
        'id', 'name', 'category', 'dynasty', 
        'visual_type', 'meaning', 
        'is_recommended', 'is_hot', 'status',
        'view_count', 'like_count', 'collect_count'
    ]
    
    # 添加更多过滤器
    list_filter = [
        'category', 'dynasty', 'status', 
        'is_recommended', 'is_hot', 'visual_type',
        'color_type', 'difficulty'
    ]
    
    search_fields = ['name', 'pinyin', 'meaning', 'story']
    
    # 允许直接在列表页编辑的字段
    list_editable = ['is_recommended', 'is_hot', 'status']
    
    list_select_related = ['category', 'dynasty']
    
    # 添加排序选项
    ordering = ['-created_at']
    
    inlines = [PatternImageInline, PatternColorInline]
    
    # 分页
    list_per_page = 20
    
    # 添加批量操作
    actions = [
        'mark_as_recommended', 'unmark_as_recommended',
        'mark_as_hot', 'unmark_as_hot',
        'mark_as_active', 'mark_as_inactive'
    ]
    
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'pinyin', 'english_name', 'category', 'dynasty')
        }),
        ('视觉特征', {
            'fields': ('visual_type', 'color_type', 'difficulty')
        }),
        ('文化内涵', {
            'fields': ('meaning', 'meaning_tags', 'story', 'origin', 'evolution', 'application')
        }),
        ('图片资源', {
            'fields': ('thumbnail', 'image_svg', 'image_hd'),
            'description': '建议缩略图尺寸：400x400px，高清图：1200x1200px以上'
        }),
        ('文物出处', {
            'fields': ('cultural_relic', 'relic_location'),
            'classes': ('collapse',)  # 可折叠
        }),
        ('统计信息', {
            'fields': ('view_count', 'like_count', 'collect_count'),
            'classes': ('collapse',),
            'description': '这些数据会自动更新'
        }),
        ('状态设置', {
            'fields': ('is_recommended', 'is_hot', 'status'),
            'classes': ('wide',)
        }),
    )
    
    # 只读字段（在详情页不能编辑）
    readonly_fields = ['view_count', 'like_count', 'collect_count']
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('category', 'dynasty')
    
    # 批量操作：标记为推荐
    def mark_as_recommended(self, request, queryset):
        updated = queryset.update(is_recommended=True)
        self.message_user(request, f'已标记 {updated} 个纹样为推荐')
    mark_as_recommended.short_description = '标记为推荐纹样'
    
    # 批量操作：取消推荐
    def unmark_as_recommended(self, request, queryset):
        updated = queryset.update(is_recommended=False)
        self.message_user(request, f'已取消 {updated} 个纹样的推荐标记')
    unmark_as_recommended.short_description = '取消推荐标记'
    
    # 批量操作：标记为热门
    def mark_as_hot(self, request, queryset):
        updated = queryset.update(is_hot=True)
        self.message_user(request, f'已标记 {updated} 个纹样为热门')
    mark_as_hot.short_description = '标记为热门纹样'
    
    # 批量操作：取消热门
    def unmark_as_hot(self, request, queryset):
        updated = queryset.update(is_hot=False)
        self.message_user(request, f'已取消 {updated} 个纹样的热门标记')
    unmark_as_hot.short_description = '取消热门标记'
    
    # 批量操作：上架
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f'已上架 {updated} 个纹样')
    mark_as_active.short_description = '上架选中纹样'
    
    # 批量操作：下架
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f'已下架 {updated} 个纹样')
    mark_as_inactive.short_description = '下架选中纹样'
    
    # 自定义保存逻辑
    def save_model(self, request, obj, form, change):
        if not obj.pinyin:
            from pypinyin import lazy_pinyin
            obj.pinyin = ''.join(lazy_pinyin(obj.name))
        super().save_model(request, obj, form, change)


@admin.register(UserDesign)
class UserDesignAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'pattern', 'is_public', 'created_at', 'thumbnail_preview']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username']
    list_select_related = ['user', 'pattern']
    readonly_fields = ['design_data', 'created_at', 'updated_at']
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.thumbnail.url)
        return '无预览图'
    thumbnail_preview.short_description = '预览图'


# 注册其他模型
@admin.register(PatternImage)
class PatternImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'pattern', 'is_main', 'description', 'order']
    list_filter = ['is_main', 'pattern']
    list_editable = ['is_main', 'order']


@admin.register(PatternColor)
class PatternColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'pattern', 'name', 'color_code', 'ratio']
    list_filter = ['pattern']
    list_editable = ['ratio']