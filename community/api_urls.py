from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list_api, name="community_post_list_api"),
    path("posts/<int:post_id>/", views.post_detail_api, name="community_post_detail_api"),
    path("posts/create/", views.post_create_api, name="community_post_create_api"),
    path("posts/<int:post_id>/like/", views.toggle_post_like_api, name="community_post_like_api"),
    path("posts/<int:post_id>/favorite/", views.toggle_post_favorite_api, name="community_post_favorite_api"),
    path("posts/<int:post_id>/comments/", views.post_comment_list_api, name="community_post_comment_list_api"),
    path("posts/<int:post_id>/comment/", views.post_comment_create_api, name="community_post_comment_create_api"),
    path("comments/<int:comment_id>/like/", views.toggle_comment_like_api, name="community_comment_like_api"),
]