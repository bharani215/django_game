from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(default=18)
    coin = models.IntegerField(default=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    profile_image = models.ImageField(
        upload_to='profile_images/',
        default='profile_images/default.png',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.user.username
    

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    fee = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class PlayerHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} played {self.tournament.name}"

class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    output = models.CharField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.output}"

class GameRecord(models.Model):
    STATUS_CHOICES = [
        ('Won', 'Won'),
        ('Lost', 'Lost'),
        ('Playing', 'Playing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempt_count = models.IntegerField()
    max_score = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status} in {self.attempt_count} attempts"