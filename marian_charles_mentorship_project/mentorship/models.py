from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee'),
    )
    role = models.CharField(max_length=10, choices=ROLES)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=200, blank=True)
    goals = models.CharField(max_length=200, blank=True)

class MentorshipRequest(models.Model):
    mentee = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=(('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Availability(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

class Session(models.Model):
    request = models.ForeignKey(MentorshipRequest, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    feedback_mentee = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    feedback_mentor = models.TextField(blank=True)
