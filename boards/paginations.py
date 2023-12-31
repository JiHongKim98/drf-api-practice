from rest_framework.exceptions import NotFound
from rest_framework.pagination import CursorPagination


class PostCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-id"

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except ValueError:
            # 커서(cursor)가 유효하지 않습니다.
            raise NotFound(self.invalid_cursor_message)
