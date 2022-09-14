from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
# Create your views here.
from .serializers import TweetSerializer, CommentSerializer
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from .permissions import IsAuthorPermission
from .models import Tweet, Comment, LikeTweet, DislikeTweet, LikeComment, DislikeComment, LikeDislikeTweet, TweetStatus, \
    CommentStatus, LikeDislikeComment
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, get_object_or_404, \
    RetrieveUpdateDestroyAPIView
from .paginations import StandardPagination


class TweetViewSet(ModelViewSet):
    serializer_class = TweetSerializer
    queryset = Tweet.objects.all()
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class CommentViewSet(ModelViewSet):
#     serializer_class = CommentSerializer
#     queryset = Comment.objects.all()
#     authentication_classes = (SessionAuthentication, TokenAuthentication)
#     permission_classes = [IsAuthorPermission, ]
#
#     def perform_create(self, serializers):
#         serializers.save(user=self.request.user)


class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user__username=user)
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(text__icontains=search)
            return queryset

    def perform_create(self, serializers):
        serializers.save(user=self.request.user,
                         tweet=get_object_or_404(Tweet, id=self.kwargs['tweet_id'])
                         )


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


class PostTweetLike(APIView):
    def get(self, request, tweet_id, status_slug):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        tweet_status = get_object_or_404(LikeDislikeTweet, slug=status_slug)
        try:
            like_dislike = LikeDislikeTweet.objects.create(tweet=tweet, user=request.user, status=tweet_status)
        except IntegrityError:
            like_dislike = LikeDislikeTweet.objects.get(tweet=tweet, user=request.user)
            like_dislike.delete()
            data = {'error': f'tweet {tweet_id} changed status by {request.user.username}'}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        else:
            data = {'message': f'tweet {tweet_id} changed status by {request.user.username}'}
            return Response(data, status=status.HTTP_201_CREATED)


class PostTweetDislike(APIView):
    def get(self, request, tweet_id, status_slug):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        tweet_status = get_object_or_404(TweetStatus, slug=status_slug)
        try:
            like_dislike = LikeDislikeTweet.objects.create(tweet=tweet, user=request.user)
        except IntegrityError:
            like_dislike = LikeDislikeTweet.objects.get(tweet=tweet, user=request.user)
            like_dislike.status = tweet_status
            like_dislike.save()
            data = {'error': f'tweet {tweet_id} changed status by {request.user.username}'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f'tweet {tweet_id} got status from {request.user.username}'}
            return Response(data, status=status.HTTP_201_CREATED)


class PostCommentLike(APIView):
    def get(self, request, comment_id, status_slug):
        comment = get_object_or_404(Comment, id=comment_id)
        comment_status = get_object_or_404(LikeDislikeComment, slug=status_slug)
        try:
            like_dislike = LikeDislikeComment.objects.create(comment=comment, user=request.user)
        except IntegrityError:
            like_dislike = LikeDislikeComment.objects.get(comment=comment, user=request.user)
            like_dislike.status = comment_status
            like_dislike.save()
            data = {'error': f'comment {comment_id} already liked by {request.user.username}'}
            return Response(data, status=status.HTTP_403_FORBIDDEN)
        else:
            data = {'message': f'comment {comment_id} liked by {request.user.username}'}
            return Response(data, status=status.HTTP_201_CREATED)


class PostCommentDislike(APIView):
    def get(self, request, comment_id, status_slug):
        comment = get_object_or_404(Comment, id=comment_id)
        comment_status = get_object_or_404(CommentStatus, slug=status_slug)
        try:
            dislike = DislikeTweet.objects.create(comment=comment, user=request.user)
        except IntegrityError:
            like_dislike = LikeDislikeComment.objects.get(comment=comment, user=request.user)
            like_dislike.status = comment_status
            like_dislike.save()
            data = {'error': f"comment {comment_id} already disliked by {request.user.username}"}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f"comment {comment_id} disliked by {request.user.username}"}
            return Response(data, status=status.HTTP_201_CREATED)
