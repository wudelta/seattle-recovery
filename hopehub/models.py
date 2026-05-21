from django.db import models
from django.contrib.auth.models import User

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    emotion = models.CharField(max_length=50, choices=[
        ('HAPPY', 'Happy'),
        ('SAD', 'Sad'),
        ('NEUTRAL', 'Neutral'),
        ('ANGRY', 'Angry'),
        ('FEARFUL', 'Fearful'),
    ])
    mood_rating = models.IntegerField(choices=[
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Neutral'),
        (4, 'High'),
        (5, 'Very High'),
    ])
    tags = models.ManyToManyField('Tag', blank=True)
    categories = models.ManyToManyField('Category', blank=True)
    image = models.ImageField(upload_to='journal_images', blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)