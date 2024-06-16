from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_tasks(tweet_id):
    from newsfeeds.services import NewsFeedService
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    #bulk create 不会触发 post save 的 signal，需要手动 push 到 cache 里面
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeeds_to_cache(newsfeed)
