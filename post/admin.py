from django.contrib import admin
from .models import TweetStatus, LikeDislikeTweet, LikeDislikeComment
# Register your models here.
admin.site.register(TweetStatus)
admin.site.register(LikeDislikeTweet)
admin.site.register(LikeDislikeComment)