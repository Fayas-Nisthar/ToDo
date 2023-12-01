from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Todos(models.Model):
    name=models.CharField(max_length=200)
    options=(
        ("todo","todo"),
        ("inprogress","inprogress"),
        ("completed","completed"),
    )
    status=models.CharField(max_length=200,choices=options,default="todo")
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    