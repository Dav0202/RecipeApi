from django.shortcuts import render
from rest_framework import viewsets,mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .models import Tag , Ingredients, Recipe

class BaseRecipeAttrViewset(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin):
    """Base viewset for recipe value"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for the curent authenticated user only"""
        return self.queryset.filter(user= self.request.user).order_by('-name')

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

    def get_queryset(self):
        """return objects for the curent authenticated user only"""
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class    
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)    
    

    
