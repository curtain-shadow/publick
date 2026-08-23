# patterns/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Dynasty(models.Model):
    """朝代"""
    name = models.CharField('朝代名称', max_length=50)
    start_year = models.IntegerField('起始年份', null=True, blank=True)
    end_year = models.IntegerField('结束年份', null=True, blank=True)
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '朝代'
        verbose_name_plural = '朝代'
        ordering = ['order', 'start_year']
    
    def __str__(self):
        return self.name

class PatternCategory(models.Model):
    """纹样分类"""
    name = models.CharField('分类名称', max_length=100)
    icon = models.CharField('图标', max_length=50, blank=True)
    description = models.TextField('描述', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父分类')
    
    class Meta:
        verbose_name = '纹样分类'
        verbose_name_plural = '纹样分类'
    
    def __str__(self):
        return self.name

class Pattern(models.Model):
    """纹样主表"""
    # 基础信息
    name = models.CharField('纹样名称', max_length=200)
    pinyin = models.CharField('拼音', max_length=200, blank=True)
    english_name = models.CharField('英文名称', max_length=200, blank=True)
    
    # 分类
    category = models.ForeignKey(PatternCategory, on_delete=models.SET_NULL, null=True, verbose_name='分类')
    dynasty = models.ForeignKey(Dynasty, on_delete=models.SET_NULL, null=True, verbose_name='朝代')
    
    # 视觉特征
    VISUAL_TYPES = [
        ('symmetry', '对称'),
        ('rotation', '旋转'),
        ('continuous', '连续'),
        ('single', '单独'),
        ('suitable', '适合'),
    ]
    visual_type = models.CharField('视觉特征', max_length=20, choices=VISUAL_TYPES, default='continuous')
    
    # 寓意
    meaning = models.CharField('寓意', max_length=200, blank=True, help_text='如：福、禄、寿、喜')
    MEANING_TAGS = [
        ('fu', '福'),
        ('lu', '禄'),
        ('shou', '寿'),
        ('xi', '喜'),
        ('cai', '财'),
        ('ji', '吉'),
        ('xiang', '祥'),
        ('ruyi', '如意'),
    ]
    meaning_tags = models.CharField('寓意标签', max_length=200, blank=True)
    
    # 颜色倾向
    COLOR_TYPES = [
        ('red_gold', '红金色系'),
        ('green_blue', '青绿色系'),
        ('black_white', '黑白灰系'),
        ('colorful', '多彩系'),
    ]
    color_type = models.CharField('色彩倾向', max_length=20, choices=COLOR_TYPES, default='colorful')
    
    # 难度等级
    DIFFICULTY = [
        (1, '简单几何纹'),
        (2, '复合花草纹'),
        (3, '复杂人物场景纹'),
    ]
    difficulty = models.IntegerField('难度等级', choices=DIFFICULTY, default=1)
    
    # 图片资源
    thumbnail = models.ImageField('缩略图', upload_to='images/thumb//')
    image_svg = models.FileField('矢量图SVG', upload_to='images/svg/', blank=True, null=True)
    image_hd = models.ImageField('高清图', upload_to='images/hd/')
    
    # 详细内容
    story = models.TextField('纹样故事', blank=True)
    origin = models.TextField('起源', blank=True)
    evolution = models.TextField('演变过程', blank=True)
    application = models.TextField('应用场景', blank=True)
    
    # 文物出处
    cultural_relic = models.CharField('文物出处', max_length=500, blank=True)
    relic_location = models.CharField('出土地点', max_length=200, blank=True)
    
    # 数据统计
    view_count = models.IntegerField('浏览次数', default=0)
    like_count = models.IntegerField('点赞次数', default=0)
    collect_count = models.IntegerField('收藏次数', default=0)
    
    # 状态
    is_recommended = models.BooleanField('推荐', default=False)
    is_hot = models.BooleanField('热门', default=False)
    status = models.BooleanField('上架', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '纹样'
        verbose_name_plural = '纹样'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 自动生成拼音
        if not self.pinyin:
            from pypinyin import lazy_pinyin
            self.pinyin = ''.join(lazy_pinyin(self.name))
        super().save(*args, **kwargs)

class PatternImage(models.Model):
    """纹样多图"""
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='images', verbose_name='纹样')
    image = models.ImageField('图片', upload_to='images/gallery/')
    is_main = models.BooleanField('主图', default=False)
    description = models.CharField('描述', max_length=200, blank=True)
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '纹样图片'
        verbose_name_plural = '纹样图片'
        ordering = ['order']

class PatternColor(models.Model):
    """纹样配色方案"""
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='colors', verbose_name='纹样')
    name = models.CharField('配色名称', max_length=100)
    color_code = models.CharField('颜色代码', max_length=20)
    ratio = models.FloatField('占比', default=0)
    
    class Meta:
        verbose_name = '配色'
        verbose_name_plural = '配色'

class UserCollection(models.Model):
    """用户收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, verbose_name='纹样')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'pattern']
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'

class UserDesign(models.Model):
    """用户设计作品"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='designs',
        verbose_name='用户'
    )
    name = models.CharField('作品名称', max_length=200)
    pattern = models.ForeignKey(
        Pattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='主纹样'
    )
    design_data = models.JSONField('设计数据', default=dict)
    thumbnail = models.CharField('缩略图', max_length=255, blank=True, default='')
    is_public = models.BooleanField('公开', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户设计'
        verbose_name_plural = '用户设计'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class UserLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'pattern']

class SystemPattern(models.Model):
    name = models.CharField(max_length=255)
    meaning = models.TextField(null=True, blank=True)  # 纹样的描述
    image = models.ImageField(upload_to='designs/thumbnails/')  # 存储推荐的图片
    source = models.CharField(max_length=50, default='system')  # 新增的 source 字段
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserPattern(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 关联用户
    name = models.CharField(max_length=255)
    meaning = models.TextField(null=True, blank=True)  # 可以保存纹样的描述
    image = models.ImageField(upload_to='user_patterns/')  # 保存上传的图片
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name