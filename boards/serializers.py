from rest_framework import serializers

from boards.models import PostModel, CommentModel


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source= 'owner.username')
    post = serializers.PrimaryKeyRelatedField(queryset= PostModel.objects.all())

    class Meta:
        model = CommentModel
        fields = '__all__'
    
    def update(self, instance, validated_data):
        validated_data.pop('post', None) # post 필드 수정 제한
        return super().update(instance, validated_data)


class PostBaseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source= 'owner.username')

    class Meta:
        model = PostModel
        fields = '__all__'


class PostDetailSerializer(PostBaseSerializer):
    comments = CommentSerializer(many= True, read_only= True, source= 'comment') # 역참조


class PostListSerializer(PostBaseSerializer):
    comments = serializers.SerializerMethodField(read_only= True)

    def get_comments(self, obj) -> int:
        return obj.comment.count() # 역참조

