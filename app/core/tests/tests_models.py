from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTest(TestCase):

    def test_create_user_with_email_sucessful(self):
        """Test creating a new user with email sucessful"""
        email = 'Dave@gmail.com'
        password = 'Goodness'
        user = get_user_model().objects.create_user(
            email = email, 
            password = password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user normalized"""
        email = 'dave@Gmail.com'
        user = get_user_model().objects.create_user(
            email = email, 
        )
        self.assertEqual(user.email,email.lower())
    
    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'123456')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user= get_user_model().objects.create_super_user(
            'email@gmail.com',
            'password'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)       