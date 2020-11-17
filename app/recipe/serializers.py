from rest_framework import serializers
from .models  import Tag,Ingredients,Recipe



class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""
    
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):
    """Serializer for tag objects """

    class Meta:
        model = Ingredients
        fields = ('id','name')
        read_only_fields = ('id',)

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects """
    ingredients= serializers.PrimaryKeyRelatedField(many=True,
                                queryset=Ingredients.objects.all())

    tag = serializers.PrimaryKeyRelatedField(many = True,
                                queryset= Tag.objects.all())
    class Meta:
        model = Recipe
        fields = ('id','title','time_minutes','price',
                  'link','tag','ingredients',)
        read_only_field = ('id',)         
    
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for a recipe""" 
    ingredients = IngredientsSerializer(many=True, read_only=True)
    tag = TagSerializer(many= True, read_only=True) 