from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from friendships.listeners import invalidate_following_cache
from accounts.services import UserService
from utils.memcached_helper import MemcachedHelper

"""
user.tweet_set == Tweet.objects.filter(user=user)

user.following_friendship_set
user.follower_friendship_set
"""


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # get all people who are following me, and order by time
            ('from_user_id', 'created_at'),
            # get all people I am following, and order by time
            ('to_user_id', 'created_at'),
        )
        # avoid following more than once
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return f'{self.from_user_id} follow {self.to_user_id}'

    @property
    def cached_from_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.from_user_id)

    @property
    def cached_to_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.to_user_id)


# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_following_cache, sender=Friendship)
post_save.connect(invalidate_following_cache, sender=Friendship)
