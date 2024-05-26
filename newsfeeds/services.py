from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
class NewsFeedService(object):

    @classmethod
    def fanout_to_follower(self, tweet):
        # followers = FriendshipService.get_followers(tweet.user)
        # we can not use forloop + query
        # for follower in followers:
        #     NewsFeed.objects.create(user=follower, tweet=tweet)

        newsfeeds = [
            # NewsFeed(user=follower, tweet=tweet)
            # this clause does not call save()
            # does not cause query
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)