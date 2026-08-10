from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Blog
from .serializers import BlogSerializer, BlogCreateUpdateSerializer
from .permissions import IsAuthorOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from drf_spectacular.utils import extend_schema, OpenApiResponse


class BlogPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


@extend_schema(
    tags=['Blog'],
    summary="List all blogs",
    description="Retrieve a paginated list of all blog posts. Supports search, filtering, and ordering.",
    responses={
        200: BlogSerializer(many=True),
    },
)
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


@extend_schema(
    tags=['Blog'],
    summary="Retrieve a blog",
    description="Retrieve the details of a specific blog post using its ID.",
    responses={
        200: BlogSerializer,
        404: OpenApiResponse(
            description="Blog not found"
        ),
    },
)
class BlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'id'


@extend_schema(
    tags=['Blog'],
    summary="Create a blog",
    description="Create a new blog post. The authenticated user is automatically assigned as the author.",
    request=BlogCreateUpdateSerializer,
    responses={
        201: BlogSerializer,
        400: OpenApiResponse(
            description="Invalid request data"
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid"
        ),
    },
)
class BlogCreateView(generics.CreateAPIView):
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        self.blog = serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)

        return Response(
            BlogSerializer(self.blog).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=['Blog'],
    summary="Update a blog",
    description="Update a blog post. Only the author of the blog can update it.",
    request=BlogCreateUpdateSerializer,
    responses={
        200: BlogSerializer,
        400: OpenApiResponse(
            description="Invalid request data"
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid"
        ),
        403: OpenApiResponse(
            description="You do not have permission to modify this blog"
        ),
        404: OpenApiResponse(
            description="Blog not found"
        ),
    },
)
class BlogUpdateView(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'id'


@extend_schema(
    tags=['Blog'],
    summary="Delete a blog",
    description="Delete a blog post. Only the author of the blog can delete it.",
    responses={
        204: None,
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid"
        ),
        403: OpenApiResponse(
            description="You do not have permission to delete this blog"
        ),
        404: OpenApiResponse(
            description="Blog not found"
        ),
    },
)
class BlogDeleteView(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'id'


@extend_schema(
    tags=['Blog'],
    summary="List my blogs",
    description="Retrieve all blog posts created by the currently authenticated user.",
    responses={
        200: BlogSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid"
        ),
    },
)
class MyBlogsView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BlogPagination

    def get_queryset(self):
        return Blog.objects.filter(author=self.request.user)

