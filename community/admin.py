from django.contrib import admin
from .models import (
    CommunityPost,
    CommunityPostMedia,
    CommunityPostLike,
    CommunityPostFavorite,
    CommunityPostComment,
    CommunityPostCommentLike,
)


class CommunityPostMediaInline(admin.TabularInline):
    model = CommunityPostMedia
    extra = 0


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'user',
        'post_type',
        'visibility',
        'status',
        'is_deleted',
        'like_count',
        'collect_count',
        'comment_count',
        'view_count',
        'created_at',
    )
    list_filter = (
        'post_type',
        'visibility',
        'status',
        'is_deleted',
        'created_at',
    )
    search_fields = (
        'title',
        'content',
        'user__username',
    )
    readonly_fields = (
        'like_count',
        'collect_count',
        'comment_count',
        'view_count',
        'created_at',
        'updated_at',
    )
    inlines = [CommunityPostMediaInline]


@admin.register(CommunityPostMedia)
class CommunityPostMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'media_type',
        'file',
        'created_at',
    )
    list_filter = (
        'media_type',
        'created_at',
    )
    search_fields = (
        'post__title',
    )


@admin.register(CommunityPostLike)
class CommunityPostLikeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'user',
        'created_at',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'post__title',
        'user__username',
    )


@admin.register(CommunityPostComment)
class CommunityPostCommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'user',
        'parent',
        'created_at',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'post__title',
        'user__username',
        'content',
    )

@admin.register(CommunityPostCommentLike)
class CommunityPostCommentLikeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'comment',
        'user',
        'created_at',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'comment__content',
        'user__username',
    )

@admin.register(CommunityPostFavorite)
class CommunityPostFavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'post',
        'user',
        'created_at',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'post__title',
        'user__username',
    )