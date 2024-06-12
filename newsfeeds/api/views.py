from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService

class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    # def get_queryset(self):
    #     # customize queryset, because check newsfeed requires permissions
    #     # only check user = current log in user's newsfeed
    #     # also could use self.request.user.newsfeed_set.all()
    #     return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        # queryset = NewsFeed.objects.filter(user=self.request.user)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(
            page,
            context={'request' : request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)