from rest_framework import serializers
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content','slug','author','created_at','updated_at']
        read_only_fields = [ 'author', 'created_at', 'updated_at' ]


class BlogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [  'title','content']