from friendships.models import Friendship
from django.conf import settings
from django.core.cache import caches
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']

class FriendshipService(object):
    @classmethod
    def get_followers(cls, user):
        # wrong method 1
        # this method would cause N + 1 queries
        # when you use filter to get all friendships, you would use 1 query
        # when you use forloop to get each from_user of friendship in friendships
        # you would use N queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        #wrong method 2
        # selected_related('from_user') would preload all from_users in friendships
        # so, when you use forloop in return , it would not cause N queries
        # but selected_related() uses JOIN, join has been baned in huge web development
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # right method 1
        # does not like getting from_user
        # friendship.from_user_id does not cause another new query request
        # because when you get friendships using Friendship.objects.filter()
        # from_user_id has been gotten
        # after you get follower_id
        # you could use only 1 query to get all followers
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # right method 2
        # prefetch_related('from_user') would generate two clauses, using in query
        # the executing SQL is like above, 2 SQL queries
        friendships = Friendship.objects.filter(
            to_user=user
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()

    """
    每次生成一个 set 后 django 会 serialize 这个 set成字符串，存入 memcached 中
    每一次调用缓存，django 会将 memcached 中的这个 set deserialize成为真正的 set
    所以 memcached 并不支持更新，你不能将一个新来的数据直接扔个 memcached
    """

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    """
    当然，你可以先把 set 从 memcach 中 read 出来，添加新的数据后再 serialize 成为字符串存回 memcached 中
    但是，在高并发的场景之下，很容易在一条数据还没更新完成的时候，并一条进程在同时更新数据，会造成错误的缓存文件
    所以通常来说，在更新数据的时候，会将原有的 cache 直接 delete，虽然也有几率造成错误，但是相对来说比更新要好
    """

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)



