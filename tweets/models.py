from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from accounts.services import UserService


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who post this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')
    @property
    def hours_to_now(self):
        #datetime.now() has no time zone info, need to add utc
        return (utc_now() - self.created_at).seconds // 3600

    # @property
    # def comments(self):
    #     return self.comment_set.all()
    #     # return Comment.objects.filter(tweet=self)

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def cached_user(self):
        return UserService.get_user_through_cache(self.user_id)


class TweetPhoto(models.Model):
    # 图片在哪个tweet下面
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # 谁上传了这张照片，这个信息虽然可以从tweet中获取，但是重复的记录在Image上面可以
    # 带来很多便利，比如某个人经常上传一些不合法的照片，那么这个人新上传的照片可以被标记为重点审查对象
    # 或者我们需要封禁某个人上传照片时，可以通过这个model快速筛选
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # 图片文件
    file = models.FileField()
    order = models.IntegerField(default=0)

    # 图片状态，用于审核等
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    """
    软删除（soft delete）标记，当一个照片被删除的时候。首先会被标记为已经删除
    在一定时间之后，才会被真正删除，这样做的目的是，如果tweet被删除的时候马上执行真删除通常回花费一定的时间
    影响效率。可以用异步任务在后台慢慢真删除
    """
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted','created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet.id} : {self.file}'
