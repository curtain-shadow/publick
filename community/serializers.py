from rest_framework import serializers
from .models import (
    CommunityPost,
    CommunityPostComment,
    CommunityPostLike,
    CommunityPostCommentLike,
    CommunityPostFavorite,
    CommunityPostMedia,
)


class CommunityPostCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    reply_to_username = serializers.CharField(source='reply_to_user.username', read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPostComment
        fields = [
            'id',
            'post',
            'user',
            'username',
            'content',
            'parent',
            'reply_to_user',
            'reply_to_username',
            'like_count',
            'is_liked',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = [
            'user',
            'post',
            'like_count',
            'created_at',
            'updated_at',
            'replies',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return CommunityPostCommentLike.objects.filter(comment=obj, user=user).exists()

    def get_replies(self, obj):
        if obj.parent_id is not None:
            return []

        children = obj.replies.filter(
            is_deleted=False,
            status='normal'
        ).select_related('user', 'reply_to_user').order_by('created_at')

        return CommunityPostCommentSerializer(
            children,
            many=True,
            context=self.context
        ).data

class CommunityPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user.username', read_only=True)
    favorite_count = serializers.IntegerField(source='collect_count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = [
            'id',
            'title',
            'content',
            'post_type',
            'visibility',
            'scene',
            'style',
            'color',
            'alt_text',
            'like_count',
            'favorite_count',
            'comment_count',
            'view_count',
            'created_at',
            'updated_at',
            'user',
            'author_name',
            'is_liked',
            'is_favorited',
            'media',
        ]
        read_only_fields = [
            'user',
            'like_count',
            'comment_count',
            'view_count',
            'created_at',
            'updated_at',
            'media',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return CommunityPostLike.objects.filter(post=obj, user=user).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return CommunityPostFavorite.objects.filter(post=obj, user=user).exists()

    def get_media(self, obj):
        medias = obj.media.all().order_by('created_at')
        return CommunityPostMediaSerializer(
            medias,
            many=True,
            context=self.context
        ).data

class CommunityPostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPostMedia
        fields = ['id', 'media_type', 'file', 'file_url', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None