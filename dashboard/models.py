# dashboard/models.py

from django.db import models
from django.contrib.auth.models import User

class GestoRegistrado(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Para saber de quem é o gesto
    nome = models.CharField(max_length=100)      # Nome que o usuário deu ao gesto (ex: "ligar luz")
    gesto = models.CharField(max_length=100)     # Nome interno do gesto (ex: "gesto_palma_aberta")
    criado_em = models.DateTimeField(auto_now_add=True)  # Quando foi criado

    def __str__(self):
        return f"{self.nome} ({self.gesto})"
