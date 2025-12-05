import uuid
import secrets

from django.db import models
from django.utils import timezone

from account.models import User


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name


class ProjectFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    attachment = models.FileField(upload_to='projectfiles')

    def __str__(self):
        return self.name
    

class ProjectNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='notes', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)  # Temporarily nullable for migration
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
        ]

    def __str__(self):
        return f"Note for {self.project.name} - {self.created_at.strftime('%Y-%m-%d')}"


class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='share_links', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='share_links', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['project', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Share link for {self.project.name} - {self.token[:16]}..."


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['project', '-timestamp']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Comment by {self.user.name or self.user.email} on {self.project.name}"


class Reminder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name='reminders', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    reminder_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='reminders', on_delete=models.CASCADE)

    class Meta:
        ordering = ['reminder_datetime']
        indexes = [
            models.Index(fields=['project', 'reminder_datetime']),
            models.Index(fields=['status', 'reminder_datetime']),
        ]

    def compute_status(self):
        """Compute status based on reminder_datetime"""
        now = timezone.now()
        if self.reminder_datetime < now:
            return 'overdue'
        elif (self.reminder_datetime - now).total_seconds() <= 86400:  # 24 hours
            return 'due_soon'
        else:
            return 'pending'

    def save(self, *args, **kwargs):
        if self.status == 'pending':  # Only auto-compute if status is pending
            self.status = self.compute_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.project.name}"