from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Voter(models.Model):
    user_fname = models.CharField(max_length=200, verbose_name='First name')
    user_lname = models.CharField(max_length=200, verbose_name='Last name')
    user_email = models.EmailField(unique=True, max_length=200, verbose_name='Email')
    password = models.CharField(max_length=200, default=True)
    has_voted = models.BooleanField(default=False)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.user_email

class Position(models.Model):
    POSITION_CHOICES = [
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Auditor', 'Auditor'),
        ('Public Information Officer', 'Public Information Officer'),
        ('Peace Officer', 'Peace Officer'),
    ]

    position = models.CharField(max_length=100, choices=POSITION_CHOICES)

    def __str__(self):
        return self.position

class Candidate(models.Model):
    name = models.CharField(max_length=100,)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.voter} voted {self.candidate} for {self.position}"