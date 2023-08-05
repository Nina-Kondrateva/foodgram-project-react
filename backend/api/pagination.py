from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомный класс пагинации."""

    page_size = 6
