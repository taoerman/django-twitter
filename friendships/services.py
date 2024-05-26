from friendships.models import Friendship
from django.contrib.auth.models import User
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