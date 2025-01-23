from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.conf import settings
from django.core.mail import send_mail
import uuid

# Create your models here.

# Models
class UserProfile(AbstractUser):
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name='userprofile_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='userprofile_permissions', blank=True)

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RSVP(models.Model):
    STATUS_CHOICES = [
        ("Going", "Going"),
        ("Maybe", "Maybe"),
        ("Not Going", "Not Going"),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()

# Serializers
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

# Permissions
class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user

class IsInvitedToPrivateEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_public:
            return RSVP.objects.filter(event=obj, user=request.user).exists()
        return True
