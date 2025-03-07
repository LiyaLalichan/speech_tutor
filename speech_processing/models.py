# models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)  # Category name (e.g., "Common Greetings")
    description = models.TextField(blank=True, null=True)  # Optional description
    order = models.IntegerField(default=0)  # For controlling display order
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

class ExpectedSpeech(models.Model):
    text = models.CharField(max_length=255)  # Keeping your existing field
    category = models.ForeignKey(Category, related_name='words', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Keeping your existing field
    order = models.IntegerField(default=0)  # For ordering words within a category
    
    def __str__(self):
        return self.text

class SpeechRecord(models.Model):
    text = models.TextField()  # Keeping your existing field
    created_at = models.DateTimeField(auto_now_add=True)  # Keeping your existing field
    expected_speech = models.ForeignKey(ExpectedSpeech, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.text[:50]