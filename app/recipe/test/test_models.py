from django.test import TestCase
from django.contrib.auth import get_user_model 
from .. import models

from unittest.mock import patch

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

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self,mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'filename.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path,exp_path)

