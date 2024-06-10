from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.paginations import FriendshipPagination
# from friendships.services import FriendshipService
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)



class FriendshipViewSet(viewsets.GenericViewSet):

    # /api/friendships/1/unfollow : current user unfollows user_id = 1
    """
    we hope /api/friendship/1/follow to follow user_id = 1
    so the queryset should be User.objects.all()
    if we use Friendship.objects.all(), will result 404 Not Found
    because the actions with detail=True will call get_object() first,
    which is queryset.filter(pk=1) to check if this pk exists.
    """
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        # AllowAny means everyone could get the followers of user_id = pk
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request':request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        # serializer = FollowingSerializer(friendships, many=True)
        # return Response({'followings' : serializer.data}, status=status.HTTP_200_OK)
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request':request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # check whether the pk exist in database or not
        self.get_object()
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success' : True,
                'duplicate' : True,
            }, status=status.HTTP_201_CREATED)
        #/api/friendships/pk/follow/
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id' : request.user.id,
            'to_user_id' : pk,
        })
        if not serializer.is_valid():
            return Response({
                'success' : False,
                'errors' : serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success' : True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        self.get_object()
        # notice, the type of pk is String, we got to transfer it to int
        if request.user.id == int(pk):
            return Response({
                'success' : False,
                'message' : 'You can not unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # there are to value when we call delete method, one value is how much data we have deleted
        # the other value is how much data we have deleted for every type
        # why we may delete so many kinds of types data?
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        # FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success' : True, 'deleted' : deleted})

    def list(self, request):
        return Response({'message' : 'this is friendships home page'})



