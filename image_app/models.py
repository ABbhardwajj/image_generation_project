# In images/models.py
from django.db import models

class GeneratedImage(models.Model):
    prompt = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.prompt
