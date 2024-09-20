from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import (AvatarSerializer, IngredientSerializer, TagSerializer,
                             UserSerializer, UserRegisterSerializer)
from recipes.models import (Ingredient, Tag)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # Разобраться с поиском
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('^name', 'name')
    search_fields = ('^name', 'name')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegisterSerializer
        return UserSerializer
    
    @action(detail=False, url_path='me')
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)


    @action(detail=False, methods=['put', 'delete'],
            url_path='me/avatar')
    def avatar(self, request):
        user = self.request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.avatar = serializer.validated_data['avatar']
            user.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
