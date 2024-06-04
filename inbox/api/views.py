from rest_framework import viewsets, status
from inbox.api.serializers import (
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from notifications.models import Notification
from utils.decorators import required_params
class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    # ListModelMixin can list all notifications
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',)

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
        # return self.request.user.notifications.all()

    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, *args, **kwargs):
        # GET /api/notifications/unread_count/
        # _ not match the rules of url
        # so use url_path='unread-count' instead of unread_count
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count' : count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, *args, **kwargs):
        updated_count = self.get_queryset().filter(unread=True).update(unread=False)
        return Response({'marked_count' : updated_count}, status=status.HTTP_200_OK)

    @required_params(method='PUT', params=['unread'])
    def update(self, request, *args, **kwargs):
        serializer = NotificationSerializerForUpdate(
            # PUT /api/notifications/id
            # because of instance = self.get_object()
            # the serializer.save() would call update() method
            # instance = self.get_object() can get the old instance
            # the update data is in the request.data
            instance=self.get_object(),
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message' : 'please check your input',
                'errors' : serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK
        )
