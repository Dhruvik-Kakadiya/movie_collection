from django.db import models
from django.contrib.auth.models import User
import uuid


class Movie(models.Model):
    """Model to store movie information"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.CharField(max_length=255, blank=True, null=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    def __str__(self):
        return self.title


class Collection(models.Model):
    """Model to store collection information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    title = models.CharField(max_length=255)
    description = models.TextField()
    movies = models.ManyToManyField(Movie, related_name='collections')
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    def __str__(self):
        return self.title


class RequestCount(models.Model):
    count = models.PositiveIntegerField(default=0)

    @staticmethod
    def get_count():
        obj, created = RequestCount.objects.get_or_create(pk=1)
        return obj.count

    @staticmethod
    def increment_count():
        obj, created = RequestCount.objects.get_or_create(pk=1)
        obj.count += 1
        obj.save()

    @staticmethod
    def reset_count():
        obj, created = RequestCount.objects.get_or_create(pk=1)
        obj.count = 0
        obj.save()
