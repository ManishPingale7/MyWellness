from django.contrib.auth.models import AbstractUser
from django.db import models


class ActivityData(models.Model):
    user_id = models.IntegerField() 
    activity_date = models.DateField()
    total_steps = models.IntegerField()
    total_distance = models.FloatField()
    very_active_distance = models.FloatField()
    moderately_active_distance = models.FloatField()
    light_active_distance = models.FloatField()
    sedentary_active_distance = models.FloatField()
    very_active_minutes = models.IntegerField()
    fairly_active_minutes = models.IntegerField()
    lightly_active_minutes = models.IntegerField()
    sedentary_minutes = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return f"User {self.user_id} - {self.activity_date}"


class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username

# choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]