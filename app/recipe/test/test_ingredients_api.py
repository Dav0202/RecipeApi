from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Ingredients,Recipe
from ..serializers import IngredientsSerializer

INGREDIENTS_URL = reverse('recipe:ingredients-list')

class PublicIngredientsApiTest(TestCase):
    """Test the Publicy avaliable ingredient API"""
    
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED
        )


class PrivateIngredientsApiTest(TestCase):
    """Test ingredients can be retrived by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testapi@api.com'
            '12345'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test Retriving ingredient list"""
        Ingredients.objects.create(
            user = self.user,
            name = 'Cucumber'
        )
        Ingredients.objects.create(
            user = self.user,
            name = 'Salt'
        )
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientsSerializer(ingredients,many=True)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'otrher@api.com'
            '1234'
        )
        Ingredients.objects.create(
            user = user2,
            name = 'carrot'
        )
        ingredient = Ingredients.objects.create(
            user = self.user,
            name = 'cowbell'
        )
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)
    
    def test_create_ingredient_sucessful(self):
        """Test creating a new ingredient"""
        payload = {'name':'carrot'}
        self.client.post(INGREDIENTS_URL,payload)
        exists = Ingredients.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invaid ingredients fails""" 
        payload = {
            'name' : '',
        }
        res = self.client.post(INGREDIENTS_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    
    def test_filtering_ingredients_assigned_to_recipe(self):
        """Test filtering ingredients by those assigned to recipe"""
        ingredients1 = Ingredients.objects.create(user= self.user, name='Corn')
        ingredients2 = Ingredients.objects.create(user= self.user, name='Beans')   
        recipe = Recipe.objects.create(
            title = 'Eat me',
            time_minutes=10,
            price = 5.00,
            user = self.user
        )
        recipe.ingredients.add(ingredients1)
        res = self.client.get(INGREDIENTS_URL,{'assigned_only': 1})

        serializer1= IngredientsSerializer(ingredients1)
        serializer2= IngredientsSerializer(ingredients2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        ingredients = Ingredients.objects.create(user= self.user, name='corn')
        Ingredients.objects.create(user= self.user, name='Beans')   
        recipe1 = Recipe.objects.create(
            title = 'Eat me',
            time_minutes=10,
            price = 5.00,
            user = self.user
        )
        recipe1.ingredients.add(ingredients)
        recipe2 = Recipe.objects.create(
            title = 'Eatre',
            time_minutes=12,
            price = 51.00,
            user = self.user
        )
        recipe2.ingredients.add(ingredients)
        res = self.client.get(INGREDIENTS_URL,{'assigned_only': 1})
        self.assertEqual(len(res.data),1)
    
    