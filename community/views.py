from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import (
    CommunityPost,
    CommunityPostMedia,
    CommunityPostLike,
    CommunityPostFavorite,
    CommunityPostComment,
    CommunityPostCommentLike,
)
from .serializers import CommunityPostSerializer, CommunityPostCommentSerializer


# 页面
def post_list_page(request):
    return render(request, 'community/post_list.html')


def post_detail_page(request, post_id):
    return render(request, 'community/detail.html', {'post_id': post_id})


def publish_page(request):
    return render(request, 'community/publish.html')

def qa_page(request):
    return render(request, "community/qa.html")

def qa_detail_page(request, post_id):
    return render(request, "community/qa_detail.html", {"post_id": post_id})

def publish_qa_page(request):
    return render(request, "community/publish.html", {"default_type": "qa"})

# 帖子列表
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_list_api(request):
    posts = CommunityPost.objects.filter(
        is_deleted=False,
        status='published',
    ).select_related('user').order_by('-created_at')

    serializer = CommunityPostSerializer(posts, many=True, context={'request': request})
    return Response({
        'code': 200,
        'message': '获取成功',
        'count': posts.count(),
        'results': serializer.data
    })


# 帖子详情
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_detail_api(request, post_id):
    post = get_object_or_404(
        CommunityPost.objects.select_related('user'),
        id=post_id,
        status='published',
        is_deleted=False,
    )

    CommunityPost.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
    post.refresh_from_db()

    serializer = CommunityPostSerializer(post, context={'request': request})
    return Response({
        'code': 200,
        'message': '获取成功',
        'data': serializer.data
    })


# 发帖
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def post_create_api(request):
    title = (request.data.get('title') or '').strip()
    content = (request.data.get('content') or '').strip()

    if not title:
        return Response({
            'code': 400,
            'message': '标题不能为空',
        }, status=status.HTTP_400_BAD_REQUEST)

    if not content:
        return Response({
            'code': 400,
            'message': '内容不能为空',
        }, status=status.HTTP_400_BAD_REQUEST)

    post = CommunityPost.objects.create(
        user=request.user,
        title=title,
        content=content,
        post_type=request.data.get('post_type', 'post') or 'post',
        visibility=request.data.get('visibility', 'public') or 'public',
        comment_status=request.data.get('comment_status', 'open') or 'open',
        status='published',
        is_deleted=False,
        scene=request.data.get('scene') or None,
        style=request.data.get('style') or None,
        color=request.data.get('color') or None,
        alt_text=request.data.get('alt_text') or '',
        design_id=request.data.get('design_id') or None,
    )

    image_file = request.FILES.get('image')
    if image_file:
        CommunityPostMedia.objects.create(
            post=post,
            file=image_file,
            media_type='image'
        )

    serializer = CommunityPostSerializer(post, context={'request': request})
    return Response({
        'code': 201,
        'message': '发帖成功',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)


# 点赞切换
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_like_api(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, is_deleted=False)
    like_obj = CommunityPostLike.objects.filter(post=post, user=request.user).first()

    if like_obj:
        like_obj.delete()
        if post.like_count > 0:
            post.like_count -= 1
            post.save(update_fields=['like_count'])
        return Response({
            'code': 200,
            'message': '已取消点赞',
            'liked': False,
            'like_count': post.like_count
        })

    CommunityPostLike.objects.create(post=post, user=request.user)
    post.like_count += 1
    post.save(update_fields=['like_count'])
    return Response({
        'code': 200,
        'message': '点赞成功',
        'liked': True,
        'like_count': post.like_count
    })


# 收藏切换（暂未启用，先避免报错）
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_favorite_api(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, is_deleted=False)
    favorite_obj = CommunityPostFavorite.objects.filter(post=post, user=request.user).first()

    if favorite_obj:
        favorite_obj.delete()
        if post.collect_count > 0:
            post.collect_count -= 1
            post.save(update_fields=['collect_count'])
        return Response({
            'code': 200,
            'message': '已取消收藏',
            'favorited': False,
            'favorite_count': post.collect_count
        })

    CommunityPostFavorite.objects.create(post=post, user=request.user)
    post.collect_count += 1
    post.save(update_fields=['collect_count'])

    return Response({
        'code': 200,
        'message': '收藏成功',
        'favorited': True,
        'favorite_count': post.collect_count
    })


# 评论列表
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_comment_list_api(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, is_deleted=False)
    comments = post.comments.filter(
        parent__isnull=True,
        is_deleted=False,
        status='normal'
    ).select_related('user', 'reply_to_user').order_by('created_at')

    serializer = CommunityPostCommentSerializer(
        comments,
        many=True,
        context={'request': request}
    )
    return Response({
        'code': 200,
        'message': '获取成功',
        'results': serializer.data
    })


# 评论提交
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def post_comment_create_api(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, is_deleted=False)

    if post.comment_status == 'closed':
        return Response({
            'code': 400,
            'message': '当前帖子已关闭评论'
        }, status=status.HTTP_400_BAD_REQUEST)

    content = (request.data.get('content') or '').strip()
    parent_id = request.data.get('parent')
    reply_to_user_id = request.data.get('reply_to_user')

    if not content:
        return Response({
            'code': 400,
            'message': '评论内容不能为空',
        }, status=status.HTTP_400_BAD_REQUEST)

    parent = None
    if parent_id:
        parent = get_object_or_404(
            CommunityPostComment,
            id=parent_id,
            post=post,
            is_deleted=False
        )

    reply_to_user = None
    if reply_to_user_id:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        reply_to_user = get_object_or_404(User, id=reply_to_user_id)

    comment = CommunityPostComment.objects.create(
        post=post,
        user=request.user,
        content=content,
        parent=parent,
        reply_to_user=reply_to_user,
        like_count=0,
        status='normal',
        is_deleted=False,
    )

    post.comment_count += 1
    post.save(update_fields=['comment_count'])

    serializer = CommunityPostCommentSerializer(comment, context={'request': request})
    return Response({
        'code': 201,
        'message': '评论成功',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def toggle_comment_like_api(request, comment_id):
    comment = get_object_or_404(
        CommunityPostComment,
        id=comment_id,
        is_deleted=False,
        status='normal'
    )

    like_obj = CommunityPostCommentLike.objects.filter(
        comment=comment,
        user=request.user
    ).first()

    if like_obj:
        like_obj.delete()
        if comment.like_count > 0:
            comment.like_count -= 1
            comment.save(update_fields=['like_count'])
        return Response({
            'code': 200,
            'message': '已取消点赞',
            'liked': False,
            'like_count': comment.like_count
        })

    CommunityPostCommentLike.objects.create(comment=comment, user=request.user)
    comment.like_count += 1
    comment.save(update_fields=['like_count'])

    return Response({
        'code': 200,
        'message': '点赞成功',
        'liked': True,
        'like_count': comment.like_count
    })