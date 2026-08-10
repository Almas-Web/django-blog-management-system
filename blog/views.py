from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Blog
from .serializers import BlogSerializer, BlogCreateUpdateSerializer
from .permissions import IsAuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class BlogPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


class BlogListView(generics.ListAPIView):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
    pagination_class = BlogPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = ['title', 'content']
    filterset_fields = ['author']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

class BlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'id'


class BlogCreateView(generics.CreateAPIView):
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class BlogUpdateView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'id'


class BlogDeleteView(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'id'


class MyBlogsView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BlogPagination

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user)