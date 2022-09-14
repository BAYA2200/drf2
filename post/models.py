from django.db import models
from account.models import User
from django.db.models.signals import pre_save, post_save
from django.db.models import Count


def like_dislike_save(sender, instance, **kwargs):
    if sender == LikeTweet:
        model = LikeTweet
    else:
        model = LikeTweet
    try:
        dislike = DislikeTweet.objects.get(tweet=instance.tweet, user=instance.user)
    except LikeTweet.DoesNotExist:
        pass
    else:
        dislike.delete()


def like_dislike_comment_save(sender, instance, **kwargs):
    if sender == LikeComment:
        model = LikeComment
    else:
        model = LikeComment
    try:
        dislike = DislikeComment.objects.get(comment=instance.comment, user=instance.user)
    except LikeComment.DoesNotExist:
        pass
    else:
        dislike.delete()


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Tweet from {self.username} at {self.updated}'

    @property
    def post_username(self):
        return self.user.username


class Tweet(Post):
    text = models.CharField(max_length=140)

    def get_status(self):
        like_dislike = LikeDislikeTweet.objects.filter(tweet=self) \
            .values("status__status_name").annotate(count=Count('status'))
        statuses = {}
        for i in like_dislike:
            statuses[i['status__status_name']] = i['count']

        return statuses

    # def get_likes(self):
    #     likes = LikeTweet.objects.filter(tweet=self)
    #     return likes.count()
    #
    # def get_dislikes(self):
    #     dislikes = DislikeTweet.objects.filter(tweet=self)
    #     return dislikes.count()

    def __str__(self):
        return f'{self.__class__.__name__} from {self.user.username} at {self.updated}'


class Comment(Post):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)

    def get_status(self):
        like_dislike = LikeDislikeComment.objects.filter(tweet=self) \
            .values("status__status_name").annotate(count=Count('status'))
        statuses = {}
        for i in like_dislike:
            statuses[i['status__status_name']] = i['count']

        return statuses

    # def get_likes(self):
    #     likes = LikeTweet.objects.filter(tweet=self)
    #     return likes.count()
    #
    # def get_dislikes(self):
    #     dislikes = DislikeTweet.objects.filter(tweet=self)
    #     return dislikes.count()

    def __str__(self):
        return f'{self.__class__.__name__} from {self.user.username} at {self.updated}'


class LikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'tweet']

    def save(self, *args, **kwargs):
        try:
            dislike = DislikeTweet.objects.get(tweet=self.tweet, user=self.user)
        except DislikeTweet.DoesNotExist:
            pass
        else:
            dislike.delete()
        super().save(*args, **kwargs)


class DislikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'tweet']

    def save(self, *args, **kwargs):
        try:
            dislike = DislikeTweet.objects.get(tweet=self.tweet, user=self.user)
        except LikeTweet.DoesNotExist:
            pass
        else:
            dislike.delete()
        super().save(*args, **kwargs)


class LikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'comment']

    def save(self, *args, **kwargs):
        try:
            dislike = DislikeComment.objects.get(comment=self.comment, user=self.user)
        except DislikeComment.DoesNotExist:
            pass
        else:
            dislike.delete()
        super().save(*args, **kwargs)


class DislikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'comment']

    def save(self, *args, **kwargs):
        try:
            dislike = DislikeComment.objects.get(comment=self.comment, user=self.user)
        except LikeComment.DoesNotExist:
            pass
        else:
            dislike.delete()
        super().save(*args, **kwargs)


class TweetStatus(models.Model):
    slug = models.CharField(max_length=20, unique=True)
    status_name = models.CharField(max_length=20)

    def __str__(self):
        return self.status_name


class LikeDislikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(TweetStatus, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'tweet']

    def __str__(self):
        return f"{self.tweet} - {self.user.username} - {self.status.status_name}"


class CommentStatus(models.Model):
    slug = models.CharField(max_length=20, unique=True)
    status_name = models.CharField(max_length=20)

    def __str__(self):
        return self.status_name


class LikeDislikeComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(CommentStatus, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'comment']

    def __str__(self):
        return f"{self.comment} - {self.user.username} - {self.status.status_name}"


post_save.connect(like_dislike_save, LikeTweet)
post_save.connect(like_dislike_save, DislikeTweet)
post_save.connect(like_dislike_comment_save, LikeComment)
post_save.connect(like_dislike_comment_save, DislikeComment)
