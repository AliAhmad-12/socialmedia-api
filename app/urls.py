from django.urls import path
from .views import *
urlpatterns = [
    # Authentiaction Routes
    path('register/',Register.as_view(),name='register'),
    path('login/',Login.as_view(),name='login'),
    path('logout/',Logout.as_view(),name='logout'),
    path('token/refresh/',CustomTokenRefreshView.as_view(),name='refresh_token'),
    path('is_authenticated/',IsAuthenticatedView.as_view(),name="is_auth"),
    path('change_password/',ChangePasswordView.as_view(),name='changepassword'),
    

    path('google/login/',GoogleLoginView.as_view(),name='google_login'),

    path('posts/',PostApiView.as_view(),name='allposts'),
    path('post/add/',PostApiView.as_view(),name='add_post'),
    path('post/update/<uuid:post_uid>/',PostApiView.as_view(),name='update_post'),
    path('posts/saved/',SavePost.as_view(),name='saved_posts'),
    path('profileuser/<int:user_id>/',ProfileUserView.as_view(),name='profileuser'),

    path('profileuser/',ProfileUserView.as_view(),name='myprofileuser'),
    path('post/like/<uuid:post_uid>/',LikePost.as_view(),name='like'),
    path('post/save/<uuid:post_uid>/',SavePost.as_view(),name='save'),
    path('post/comment/add/<uuid:post_id>/',CommentApiView.as_view(),name='add_comment'),
    path('post/delete/<uuid:post_id>/',PostApiView.as_view(),name='delete_post'),
    path('post/comment/delete/<uuid:comment_id>/',CommentApiView.as_view(),name='delete_comment'),
    path('user/follow/<int:user_id>/',FollowUser.as_view(),name='follow'),
    path('user/following/',FollowUser.as_view(),name='following'),
    path('myposts/',MyPostsView.as_view(),name='myposts'),
    path('posts/<int:user_id>/',MyPostsView.as_view(),name='postsforuser'),
    path('suggestion/',SuggestionView.as_view(),name='suggestion'),

    # paths for chat
    path('start/',StartChat.as_view(), name='start_convo'),
    path('<int:chat_id>/',get_conversation.as_view(), name='get_conversation'),
    path('chats/',Conversations.as_view(), name='conversations'),
    path('message/<int:message_id>/update/',UpdateMessage.as_view(),name='message_update'),
    path('message/<int:message_id>/delete/',DeleteMessage.as_view(),name='message_delete')
]
