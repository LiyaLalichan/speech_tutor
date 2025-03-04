from django.db import models

class SpeechRecord(models.Model):
    text = models.TextField()  # Stores recognized speech
    created_at = models.DateTimeField(auto_now_add=True)  # Stores timestamp

    def __str__(self):
        return self.text[:50]  # Show first 50 characters in admin pane

class ExpectedSpeech(models.Model):
    text = models.CharField(max_length=255)  # Correct pronunciation text
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.text
