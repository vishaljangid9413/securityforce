from django.db import models

class FAQ(models.Model):
    category = models.CharField(max_length=50)
    question = models.CharField(max_length=150)
    answer = models.TextField(max_length=500)
    is_active = models.BooleanField(default=True)

    # def __str__(self):
    #     reutrn = f"{self.question}"
