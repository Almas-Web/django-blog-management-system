from django.urls import path

from .views import (
    BlogListView,
    BlogDetailView,
    BlogCreateView,
    BlogUpdateView,
    BlogDeleteView,
    MyBlogsView,
    BlogSummaryView,
)


urlpatterns = [
    path('', BlogListView.as_view(), name='blog-list'),

    path('create/', BlogCreateView.as_view(), name='blog-create'),

    path('<int:id>/', BlogDetailView.as_view(), name='blog-detail'),

    path('<int:id>/update/', BlogUpdateView.as_view(), name='blog-update'),

    path('<int:id>/delete/', BlogDeleteView.as_view(), name='blog-delete'),

    path(
        '<int:id>/summarize/',
        BlogSummaryView.as_view(),
        name='blog-summarize',
    ),

    path('my-blogs/', MyBlogsView.as_view(), name='my-blogs'),
]