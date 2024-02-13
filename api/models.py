from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
   pass


class Product(models.Model):
   name = models.CharField(max_length=255)
   description = models.TextField()
   image = models.ImageField()

   def __str__(self):
      return self.name
   

class SearchEntry(models.Model):
   made_by = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='search_history')
   product = models.ForeignKey(Product,on_delete = models.CASCADE,related_name='searched')
   timestamp = models.DateTimeField()

   def __str__(self):
      return f"{self.made_by} Searched for {self.product.name} on {self.timestamp}"
   
class Store(models.Model):
   name = models.CharField(max_length=255)
   link = models.URLField()

   def __str__(self):
      return self.name
   
class ProductPrice(models.Model):
   price = models.DecimalField(max_digits=10, decimal_places=2)
   product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="prices")
   store = models.ForeignKey(Store,on_delete=models.CASCADE)

   def __str__(self):
      return f"Product: {self.product} has Price: {self.price} in Store: {self.store}"