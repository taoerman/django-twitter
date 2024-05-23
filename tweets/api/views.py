from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.models import Tweet
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate

class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]
    def list(self, request):
        # do not list all tweets, must give user_id
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)

        #select * from twitter_tweets
        #where user_id = xxx oder_by created_at desc
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')
        #normally, the type of JSON Response is hash
        #can not use list
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets' : serializer.data})

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
        return Response(TweetSerializer(tweet).data, status=201)