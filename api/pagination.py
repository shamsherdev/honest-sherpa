from rest_framework.pagination import PageNumberPagination
from .pagination import HelpPagination

class Pagination:
    paginat=PageNumberPagination()
    paginat.page_size=5
    paginat.page_size_query_param='page_size'