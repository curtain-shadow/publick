from django.urls import path
from . import views

urlpatterns = [
    # 页面路由
    path("posts/", views.post_list_page, name="community_post_list_page"),
    path("posts/<int:post_id>/", views.post_detail_page, name="community_post_detail_page"),
    path("publish/", views.publish_page, name="community_post_publish_page"),

    path("qa/", views.qa_page, name="community_qa_page"),
    path("qa/<int:post_id>/", views.qa_detail_page, name="community_qa_detail_page"),
    path("publish/qa/", views.publish_qa_page, name="community_publish_qa_page"),

    # API 路由
    path("api/community/posts/", views.post_list_api, name="community_post_list_api"),
    path("api/community/posts/<int:post_id>/", views.post_detail_api, name="community_post_detail_api"),
    path("api/community/posts/create/", views.post_create_api, name="community_post_create_api"),
    path("api/community/posts/<int:post_id>/like/", views.toggle_post_like_api, name="community_post_like_api"),
    path("api/community/posts/<int:post_id>/favorite/", views.toggle_post_favorite_api, name="community_post_favorite_api"),
    path("api/community/posts/<int:post_id>/comments/", views.post_comment_list_api, name="community_post_comment_list_api"),
    path("api/community/posts/<int:post_id>/comment/", views.post_comment_create_api, name="community_post_comment_create_api"),
    path("api/community/comments/<int:comment_id>/like/", views.toggle_comment_like_api, name="community_comment_like_api"),
]