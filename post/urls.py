from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tweet', views.TweetViewSet, basename='tweet')
# router.register('comment', views.CommentViewSet, basename='comment')
urlpatterns = [
    path('', include(router.urls)),
    path("tweet/<int:tweet_id>/comments/", views.CommentListCreateAPIView.as_view()),
    path("tweet/<int:tweet_id>/comments/<int:pk>/", views.CommentListCreateAPIView.as_view()),
    path("tweet/<int:tweet_id>/like/", views.CommentListCreateAPIView.as_view()),
    path("tweet/<int:tweet_id>/dislike/", views.CommentListCreateAPIView.as_view()),
    path("comment/<int:comment_id>/dislike/", views.CommentListLikeDislikeCreateAPIView.as_view()),
    path("comment/<int:comment_id>/like/", views.CommentListLikeDislikeCreateAPIView.as_view()),

]
