from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.models import Tweet
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithDetail,
)
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService

class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request):
        # GET request.query_params
        # POST request.data
        # do not list all tweets, must give user_id
        #select * from twitter_tweets
        #where user_id = xxx oder_by created_at desc
        # tweets = Tweet.objects.filter(
        #     user_id=request.query_params['user_id']
        # ).order_by('-created_at')
        # tweets = TweetService.get_cached_tweets(user_id=request.query_params['user_id'])
        # tweets = self.paginate_queryset(tweets)
        #normally, the type of JSON Response is hash
        #can not use list
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            # 这句查询会被翻译为
            # select * from twitter_tweets
            # where user_id = xxx
            # order by created_at desc
            # 这句 SQL 查询会用到 user 和 created_at 的联合索引
            # 单纯的 user 索引是不够的
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request' : request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # tweet = self.get_object()
        serializer = TweetSerializerWithDetail(
            self.get_object(),
            context={'request' : request},
        )
        return Response(serializer.data)
        # return Response(
        #     TweetSerializerWithDetail(
        #         tweet,
        #         context={'request' : request}
        #     ).data
        # )

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context = {'request' : request}
        )

        if not serializer.is_valid():
            return Response({
                'success' : False,
                'message' : 'Please check input',
                'errors' : serializer.errors,
            }, status=400)
        #save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request' : request}).data,
            status=201
        )