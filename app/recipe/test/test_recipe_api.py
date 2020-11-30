from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework import serializers
from rest_framework.test import APIClient
from ..models import Recipe, Tag, Ingredients
from ..serializers import RecipeSerializer, RecipeDetailSerializer
import tempfile
import os
from PIL import Image

RECIPE_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """Return url for image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id ])

def sample_tag(user,name='main course'):
     """Create and return a sample tag"""
     return Tag.objects.create(
         user = user,
         name = name
     )

def sample_ingredients(user, name='carrot'):
    """Create and return a sample tag"""
    return Ingredients.objects.create(
        user= user,
        name =name
    )
def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price' : 5.00,
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """Test unauthorized recipe Api access"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateRecipeApiTest(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'api@api.com'
            '12345'
        )
        self.client.force_authenticate(self.user)
        

    def test_retreiving_recipies(self):  
        """Test retrieivng recipe"""
        sample_recipe(user= self.user)
        sample_recipe(user = self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many= True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    
    def test_recipies_limited_to_users(self):  
        """Test retrieivng recipe limited to user"""
        user2 = get_user_model().objects.create_user(
            'api23@api.com'
            '123435'
        )
        sample_recipe(user= user2)
        sample_recipe(user = self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes, many= True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        self.assertEqual(len(res.data),1)


    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredients(user=self.user))
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        
        self.assertEqual(res.data,serializer.data)
    
    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload ={
            'title': 'chocolate cake',
            'time_minutes': 30,
            'price': 4.00,
        }
        res = self.client.post(RECIPE_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name ='vegan')
        tag2 = sample_tag(user=self.user,name='weird food')
        payload ={
            'title': 'chocolate cake',
            'tag': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 42.00
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tag.all()
        self.assertEqual(tags.count(),2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)

    def create_recipe_with_ingredient(self):
        """Test creating a recipe with ingredients"""
        ingredients1 = sample_ingredients(user=self.user,name='Carrot')
        ingredients2 = sample_ingredients(user=self.user, name='banana')
        payload= {
            'title': 'fruit salad',
            'ingredients':[ingredients1.id, ingredients2.id],
            'time_minutes': 10,
            'price': 100.00
        }
        res = self.client.post(RECIPE_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Ingredients.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ingredients1,ingredients)
        self.assertIn(ingredients1,ingredients)
    
    def test_partial_update_recipe(self):
        """Test updating the object with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tag.add(sample_tag(user = self.user))
        new_tag = sample_tag(user = self.user, name='yam')
        payload= {
            'title': 'fruits salads',
            'tag': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        tags = recipe.tag.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating the objects with put"""
        recipe = sample_recipe(user = self.user)
        recipe.tag.add(sample_tag(user= self.user))
        payload={
             'title': 'fruit salad',
            'time_minutes': 40,
            'price': 140.00
        } 

        url = detail_url(recipe.id)
        self.client.put(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.time_minutes,payload['time_minutes'])
        self.assertEqual(recipe.price,payload['price'])
        tags = recipe.tag.all()
        self.assertEqual(tags.count(),0)

class RecipeImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@api.com'
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB',(10,10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url,{'image':ntf}, format='multipart')
            
            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code,status.HTTP_200_OK)
            self.assertIn('image',res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_bad_image(self):
        """Test uploading a bad or invalid image"""
        url = (image_upload_url(self.recipe.id))
        res = self.client.post(url,{'image':'not image'},format='multipart')        

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tag(self):
        """Test returning recipes with specific tags"""
        recipe1 = sample_recipe(user=self.user, title='Yam and egg')
        recipe2 = sample_recipe(user=self.user, title='egg sauce')
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Snacks')
        recipe1.tag.add(tag1)
        recipe2.tag.add(tag2)
        recipe3 = sample_recipe(user= self.user, title='Fish and chips')
        res = self.client.get(RECIPE_URL,{'tag': f'{tag1.id},{tag2.id}'})
  
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
    
        self.assertIn(serializer1.data,res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data,res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title='bread and egg')
        recipe2 = sample_recipe(user=self.user, title='egg stew')
        ingredient1 = sample_ingredients(user=self.user, name = 'Egg')
        ingredient2 = sample_ingredients(user =self.user, name= 'tomatoes')
        recipe3 = sample_recipe(user=self.user, title= 'Rice and spag')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        
        res = self.client.get(RECIPE_URL,{'ingredients':f'{ingredient1.id},{ingredient2.id}'})
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data,res.data)
        self.assertIn(serializer2.data,res.data)
        self.assertNotIn(serializer3.data,res.data)
