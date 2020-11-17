from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Tag
from ..serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """Test the publicly avaliable tags API"""
    def setUp(self):
        self.client= APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """"Test the public avalible tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'da@enail.com',
            '12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retriving tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name= 'dessert')
        
        res = self.client.get(TAGS_URL)

        tags= Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_tags_limited_to_user(self):
        """"Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
             'dafdfnail.com',
             '12345'
        )
        Tag.objects.create(
            user = user2,
            name = 'vegan'
        )
        tag = Tag.objects.create(user= self.user, name= 'comfort food')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'],tag.name)

    def test_create_tag_sucessful(self):
        """test creating a new tag"""
        payload = {
            'name':'test tag'
        }
        res = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload ={
            'name':''
        }
        res = self.client.post(TAGS_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)




