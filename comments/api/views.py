from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from comments.models import Comment
from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate
)
from rest_framework.response import Response
from utils.permissions import IsObjectOwner
from utils.decorators import required_params
from inbox.services import NotificationService

class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',  )

    # POST /api/comments/ -> create
    # GET /api/comments/?tweet_id= -> list
    # Get /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # 这种写法在后期需要添加其他属性进行筛选就很方便
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        serializer = CommentSerializer(
            comments,
            context={'request' : request},
            many=True,
        )
        return Response({
            'comments' : serializer.data,
        }, status=status.HTTP_200_OK)



    def create(self, request, *args, **kwargs):
        data = {
            'user_id' : request.user.id,
            'tweet_id' : request.data.get('tweet_id'),
            'content' : request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message' : 'please check input',
                'errors' : serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context={'request':request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object 是 DRF 包装的一个函数， 会在找不到的时候 raise 404 error
        #所以这里无需做额外判断
        # if we don't write instance == , serializer will call create method
        # if we write instance == , serializer will call update method
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message' : 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        #.save / if you input instance, save will call update
        # if you ddo not input instance, save will call create
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request':request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # the return value of destroy in DRF is status_code = 204 no content
        # here return success=True would be more clear, so return 200 better
        return Response({
            'success' : True,
        }, status=status.HTTP_200_OK)

