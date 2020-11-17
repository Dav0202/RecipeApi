from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Ingredients
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

