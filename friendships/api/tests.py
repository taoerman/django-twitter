from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTest(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu', 'linghu@gmail.com')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie', 'dongxie@gmail.com')
        self.domgxie_client = APIClient()
        self.domgxie_client.force_authenticate(self.dongxie)

        # create followings and followers for dongxie
        for i in range(2):
            follower = self.create_user('dongxie_follower{}'.format(i), 'dongxie@gmail.com')
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)
        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i), 'dongxie@gmail.com')
            Friendship.objects.create(from_user=self.dongxie, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.linghu.id)

        # have to log in, can follow others
        response = self.anonymous_client.post(url)
        self.assertEquals(response.status_code, 403)
        # can not use GET to follow others
        response = self.domgxie_client.get(url)
        self.assertEqual(response.status_code, 405)
        #can not follow yourself
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow successfully
        response = self.domgxie_client.post(url)
        self.assertEqual(response.status_code, 201)
        #follow repeat, success default
        response = self.domgxie_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)
        # following follows follower, which will create new data
        count = Friendship.objects.count()
        response = self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.linghu.id)

        # if you want to unfollow someone, you got to log in
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # you can not use GET to unfollow
        response = self.domgxie_client.get(url)
        self.assertEqual(response.status_code, 405)
        # you can not unfollow yourself
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow successfully
        Friendship.objects.create(from_user=self.dongxie, to_user=self.linghu)
        count = Friendship.objects.count()
        response =  self.domgxie_client.post(url)
        self.assertURLEqual(response.status_code, 200)
        self.assertURLEqual(Friendship.objects.count(), count - 1)
        # if you did not follow someone, your unfollow would be default
        count = Friendship.objects.count()
        response = self.domgxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertURLEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.dongxie.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # make sure order by time
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertURLEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'dongxie_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'dongxie_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'dongxie_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.dongxie.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # make sure order by time
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'dongxie_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'dongxie_follower0',
        )

