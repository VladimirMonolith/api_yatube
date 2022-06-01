from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets

from posts.models import Group, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, FollowSerializer, GroupSerializer, PostSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Post."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )

    def perform_create(self, serializer):
        """Создает запись, где автором является текущий пользователь."""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обьектов модели Group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    )

    def get_post(self):
        """Возвращает объект текущей записи."""
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)

    def get_queryset(self):
        """Возвращает queryset c комментариями для текущей записи."""
        return self.get_post().comments.all()

    def perform_create(self, serializer):
        """Создает комментарий для текущего поста,
        где автором является текущий пользователь."""
        serializer.save(
            author=self.request.user,
            post=self.get_post()
        )


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Вьюсет для обьектов модели Follow."""

    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        """Возвращает queryset c подписками для текущего пользователя."""
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        """Создает подписку, где подписчиком является текущий пользователь."""
        serializer.save(user=self.request.user)
