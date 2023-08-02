from rest_framework import mixins, viewsets


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """Mixins для GET запроса."""
    pass
