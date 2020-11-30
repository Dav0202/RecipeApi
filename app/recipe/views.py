from django.db.models import query
from rest_framework import viewsets,mixins,status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .models import Tag , Ingredients, Recipe
from rest_framework.decorators import action
from rest_framework.response import Response

class BaseRecipeAttrViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin):
    """Base viewset for recipe value"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for the curent authenticated user only"""
        assigned_only= bool(
            int(self.request.query_params.get('assigned_only',0))
        )
        queryset =self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull =False)
        return queryset.filter(
            user= self.request.user
            ).order_by('-name').distinct()


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)    
       
    

class TagViewSet(BaseRecipeAttrViewset):
    """Manage tags in the database"""
    #Everything was summarized Refactor Tags and ingredient
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientsViewSet(BaseRecipeAttrViewset):
    """Manage ingredients in the database"""

    queryset = Ingredients.objects.all()
    serializer_class = serializers.IngredientsSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipe in the database"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self,qs):
        """Convert a list to string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """return objects for the curent authenticated user only"""
        tag = self.request.query_params.get('tag')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tag:
            tag_ids = self._params_to_ints(tag)
            queryset = queryset.filter(tag__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
                
        return self.serializer_class    
        

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe= self.get_object()
        serializer = self.get_serializer(
            recipe,
            data = request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status= status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status= status.HTTP_400_BAD_REQUEST
        )    

    
