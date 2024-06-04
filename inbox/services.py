from django.contrib.contenttypes.models import ContentType
from tweets.models import Tweet
from notifications.signals import notify
from comments.models import  Comment
class NotificationService(object):

    @classmethod
    def send_like_notification(cls, like):
        #  content_object = GenericForeignKey('content_type', 'object_id')
        # content_object would return the type of content and the id of this object
        target = like.content_object
        if like.user == target.user:
            return
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            notify.send(
                like.user,
                recipient=target.user,
                verb='like your tweet',
                target=target,
            )
        if like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='like your comment',
                target=target,
            )


    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user == comment.tweet.user:
            return
        notify.send(
            comment.user,
            recipient=comment.tweet.user,
            verb='commented on your tweet',
            target=comment.tweet,
        )

