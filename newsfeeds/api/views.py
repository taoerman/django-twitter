from rest_framework import viewsets, status
from newsfeeds.models import NewsFeed
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.api.serializers import NewsFeedSerializer

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # customize queryset, because check newsfeed requires permissions
        # only check user = current log in user's newsfeed
        # also could use self.request.user.newsfeed_set.all()
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            context={'request' : request},
            many=True,
        )
        return Response({
            'newsfeeds' : serializer.data,
        }, status=status.HTTP_200_OK)