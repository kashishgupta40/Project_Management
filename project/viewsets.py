from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ShareLink, Comment, Reminder, ProjectNote, Project
from .serializers import (
    ShareLinkSerializer, CommentSerializer, ReminderSerializer, ProjectNoteSerializer
)
from account.models import User


class ProjectNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing project notes"""
    serializer_class = ProjectNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter notes by project_id"""
        queryset = ProjectNote.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            # Verify user has access to the project
            project = get_object_or_404(Project, id=project_id)
            if project.created_by != self.request.user:
                # Check if user has access via share link (future enhancement)
                pass
        else:
            # Only show notes for user's projects
            queryset = queryset.filter(project__created_by=self.request.user)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Set the project when creating a note"""
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        # Verify ownership
        if project.created_by != self.request.user:
            raise PermissionDenied("You don't have permission to add notes to this project.")
        serializer.save(project=project)

    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ShareLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for managing share links"""
    serializer_class = ShareLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter share links by project_id and user"""
        queryset = ShareLink.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        else:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Set the created_by user when creating a share link"""
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        # Verify ownership
        if project.created_by != self.request.user:
            raise PermissionDenied("You don't have permission to share this project.")
        serializer.save(project=project, created_by=self.request.user)

    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing project comments"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter comments by project_id"""
        queryset = Comment.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        else:
            queryset = queryset.filter(project__created_by=self.request.user)
        return queryset.order_by('-timestamp')

    def perform_create(self, serializer):
        """Set the user when creating a comment"""
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        # Verify ownership
        if project.created_by != self.request.user:
            raise PermissionDenied("You don't have permission to comment on this project.")
        serializer.save(project=project, user=self.request.user)

    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reminders"""
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter reminders by project_id and update statuses"""
        queryset = Reminder.objects.all()
        project_id = self.request.query_params.get('project_id', None)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        else:
            queryset = queryset.filter(created_by=self.request.user)

        # Update statuses for pending reminders
        now = timezone.now()
        for reminder in queryset.filter(status__in=['pending', 'due_soon']):
            if reminder.reminder_datetime < now:
                reminder.status = 'overdue'
                reminder.save(update_fields=['status'])
            elif (reminder.reminder_datetime - now).total_seconds() <= 86400:
                if reminder.status != 'overdue':
                    reminder.status = 'due_soon'
                    reminder.save(update_fields=['status'])

        return queryset.order_by('reminder_datetime')

    def perform_create(self, serializer):
        """Set the created_by user when creating a reminder"""
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        # Verify ownership
        if project.created_by != self.request.user:
            raise PermissionDenied("You don't have permission to create reminders for this project.")
        
        reminder = serializer.save(project=project, created_by=self.request.user)
        # Compute initial status
        reminder.status = reminder.compute_status()
        reminder.save(update_fields=['status'])

    def get_serializer_context(self):
        """Add request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

