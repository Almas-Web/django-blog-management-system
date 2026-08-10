from django.urls import path
from .views import (
    BlogListView,
    BlogDetailView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
    MyBlogsView
)

urlpatterns = [
    path('', BlogListView.as_view(), name='blog-list'),
    path('create/', BlogCreateView.as_view(), name='blog-create'),
    path('<int:id>/', BlogDetailView.as_view(), name='blog-detail'),
    path('update/<int:id>/', BlogUpdateView.as_view(), name='blog-update'),
    path('delete/<int:id>/', BlogDeleteView.as_view(), name='blog-delete'),
    path('my-blogs/', MyBlogsView.as_view(), name='my-blogs'),
]