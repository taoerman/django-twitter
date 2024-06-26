from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper
from newsfeeds.tasks import fanout_newsfeeds_tasks
class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        result = fanout_newsfeeds_tasks.delay(tweet.id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeeds_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
