from django.db import models
from django.contrib.auth.models import User

class Conta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)  # <- ligação com User
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    amazon_user_id = models.CharField(max_length=255, unique=True)