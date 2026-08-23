from django.conf import settings
from django.db import models


class CommunityPost(models.Model):
    POST_TYPE_CHOICES = (
        ('post', '普通帖子'),
        ('qa', '问答'),
    )

    VISIBILITY_CHOICES = (
        ('public', '公开'),
        ('private', '私密'),
    )

    COMMENT_STATUS_CHOICES = (
        ('open', '允许评论'),
        ('closed', '关闭评论'),
    )

    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts',
        verbose_name='作者'
    )
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    post_type = models.CharField(
        max_length=50,
        choices=POST_TYPE_CHOICES,
        default='post',
        verbose_name='帖子类型'
    )

    scene = models.CharField(max_length=50, blank=True, null=True, verbose_name='场景')
    style = models.CharField(max_length=50, blank=True, null=True, verbose_name='风格')
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name='配色')
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name='替代文本')

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name='可见性'
    )
    comment_status = models.CharField(
        max_length=20,
        choices=COMMENT_STATUS_CHOICES,
        default='open',
        verbose_name='评论状态'
    )

    design_id = models.BigIntegerField(blank=True, null=True, verbose_name='关联设计ID')

    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    comment_count = models.PositiveIntegerField(default=0, verbose_name='评论数')
    view_count = models.PositiveIntegerField(default=0, verbose_name='浏览数')
    collect_count = models.PositiveIntegerField(default=0, verbose_name='收藏数')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='published',
        verbose_name='发布状态'
    )
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'community_post'
        ordering = ['-created_at']
        verbose_name = '社区帖子'
        verbose_name_plural = '社区帖子'

    def __str__(self):
        return self.title


class CommunityPostMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', '图片'),
        ('video', '视频'),
    )

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name='所属帖子'
    )
    file = models.FileField(
        upload_to='community/posts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='媒体文件'
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='image')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_media'
        verbose_name = '帖子媒体'
        verbose_name_plural = '帖子媒体'

    def __str__(self):
        return f'{self.post_id} - {self.media_type}'


class CommunityPostLike(models.Model):
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='帖子'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_post_likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_like'
        unique_together = ('post', 'user')
        verbose_name = '帖子点赞'
        verbose_name_plural = '帖子点赞'

    def __str__(self):
        return f'{self.user} 点赞 {self.post_id}'


class CommunityPostComment(models.Model):
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('hidden', '隐藏'),
    )

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='帖子'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_post_comments',
        verbose_name='评论用户'
    )
    content = models.TextField(verbose_name='评论内容')

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='父评论'
    )

    reply_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replied_comments',
        verbose_name='回复目标用户'
    )

    like_count = models.PositiveIntegerField(default=0, verbose_name='点赞数')

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal',
        verbose_name='状态'
    )

    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'community_post_comment'
        ordering = ['created_at']
        verbose_name = '帖子评论'
        verbose_name_plural = '帖子评论'

    def __str__(self):
        return f'评论{self.id} - 帖子{self.post_id}'

class CommunityPostCommentLike(models.Model):
    comment = models.ForeignKey(
        CommunityPostComment,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='评论'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_post_comment_likes',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_comment_like'
        unique_together = ('comment', 'user')
        verbose_name = '评论点赞'
        verbose_name_plural = '评论点赞'

    def __str__(self):
        return f'{self.user} 点赞评论 {self.comment_id}'

class CommunityPostFavorite(models.Model):
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='帖子'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_post_favorites',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'community_post_favorite'
        unique_together = ('post', 'user')
        verbose_name = '帖子收藏'
        verbose_name_plural = '帖子收藏'

    def __str__(self):
        return f'{self.user} 收藏 {self.post_id}'