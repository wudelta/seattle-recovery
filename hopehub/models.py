from django.db import models
from django.contrib.auth.models import User

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 12 detailed string options matching the frontend layout
    emotion = models.CharField(max_length=50, choices=[
        ('joyful', 'Joyful'),
        ('peaceful', 'Peaceful'),
        ('grateful', 'Grateful'),
        ('hopeful', 'Hopeful'),
        ('balanced', 'Balanced'),
        ('reflective', 'Reflective'),
        ('anxious', 'Anxious'),
        ('sad', 'Sad'),
        ('frustrated', 'Frustrated'),
        ('angry', 'Angry'),
        ('tired', 'Tired'),
        ('overwhelmed', 'Stressed'),
    ])
    
    # Granular 10-point behavioral rating matrix
    mood_rating = models.IntegerField(choices=[
        (1, 'Crisis / Extremely Low'),
        (2, 'Very Low / Severe Distress'),
        (3, 'Low / Visibly Struggling'),
        (4, 'Mildly Low / Flat'),
        (5, 'Neutral / Baseline'),
        (6, 'Mildly Good / Stable'),
        (7, 'Good / Positive'),
        (8, 'Very Good / High Energy'),
        (9, 'Excellent / Vibrant'),
        (10, 'Peak Joy / Triumphant'),
    ])
    
    tags = models.ManyToManyField('Tag', blank=True)
    categories = models.ManyToManyField('Category', blank=True)
    image = models.ImageField(upload_to='journal_images', blank=True, null=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
