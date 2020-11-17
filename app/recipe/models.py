from django.db import models
from django.conf import settings    

class Tag(models.Model):
    "Custom tag to be used for recipe"
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE
    )

    def __str__(self):
        return self.name

class Ingredients(models.Model):
    """Custom ingredient to be used for recipe"""
    name = models.CharField(max_length = 255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE
    )
    def __str__(self):
        return self.name

class Recipe(models.Model):
    """Recipe object""" 
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )      
    title = models.CharField(max_length = 255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length = 255, blank=True)
    ingredients = models.ManyToManyField('Ingredients')
    tag = models.ManyToManyField('Tag')


    def __str__(self):
        return self.title
