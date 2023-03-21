from django.db import models
from django.contrib.auth.models import User

class Portfolio(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')      
    currency = models.CharField(max_length=10)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username
