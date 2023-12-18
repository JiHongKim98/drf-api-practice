from rest_framework import generics
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from boards.models import PostModel, CommentModel
from .serializers import PostModelSerializer, CommentModelSerializer
from .permissions import IsOwnerOrReadOnly


# GET(List), POST
class PostListCreateAPIView(generics.ListCreateAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]
    
    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.pk
        return super().create(request, *args, **kwargs)


# GET(Retrieve), UPDATE, DELETE
class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        request.data['owner'] = request.user.pk
        return super().update(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostModelSerializer(instance)
        comment_instance = instance.post_comment.all() # related_name 으로 역참조
        comment_serializer = CommentModelSerializer(comment_instance, many= True)
        data = {
            "board": serializer.data,
            "comment": comment_serializer.data
        }

        return Response(data)


class CommentCreateAPIView(generics.CreateAPIView):
    queryset = CommentModel.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.pk
        return super().create(request, *args, **kwargs)

    
class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommentModel.objects.all()
    serializer_class = CommentModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        request.data['owner'] = request.user.pk
        return super().update(request, *args, **kwargs)

