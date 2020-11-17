from django.test import TestCase
from django.contrib.auth import get_user_model 
from .. import models

def sample_user(email= 'test@email.com',password = '43322'):
    """create sample user"""
    return get_user_model().objects.create_user(email,password)

class ModelTest(TestCase):

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )
        self.assertEqual(str(tag),tag.name)

    def test_ingredient_str(self):
        """Test the ingrident string representation"""
        ingredient = models.Ingredients.objects.create(
            user = sample_user(),
            name = 'cucumber'
        )
        self.assertEqual(str(ingredient),ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Yam and egg',
            time_minutes=5,
            price=5.00,    
        ) 
        self.assertEqual(str(recipe),recipe.title)