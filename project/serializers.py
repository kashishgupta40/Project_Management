from rest_framework import serializers
from .models import ShareLink, Comment, Reminder, ProjectNote, Project
from account.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class ProjectNoteSerializer(serializers.ModelSerializer):
    """Serializer for ProjectNote model"""
    class Meta:
        model = ProjectNote
        fields = ['id', 'project', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShareLinkSerializer(serializers.ModelSerializer):
    """Serializer for ShareLink model"""
    share_url = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()
    mailto_url = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = ShareLink
        fields = ['id', 'project', 'project_name', 'token', 'share_url', 'whatsapp_url', 
                  'mailto_url', 'created_at', 'is_active', 'created_by', 'created_by_name']
        read_only_fields = ['id', 'token', 'created_at', 'created_by']

    def get_share_url(self, obj):
        """Generate shareable URL"""
        request = self.context.get('request')
        if request:
            base_url = request.build_absolute_uri('/')
            return f"{base_url}projects/shared/{obj.token}/"
        return f"/projects/shared/{obj.token}/"

    def get_whatsapp_url(self, obj):
        """Generate WhatsApp share URL"""
        from urllib.parse import quote
        request = self.context.get('request')
        if request:
            share_url = request.build_absolute_uri(f'/projects/shared/{obj.token}/')
        else:
            share_url = f"/projects/shared/{obj.token}/"
        message = f"Check out this project: {obj.project.name}\n{share_url}"
        return f"https://wa.me/?text={quote(message)}"

    def get_mailto_url(self, obj):
        """Generate mailto URL"""
        from urllib.parse import quote
        request = self.context.get('request')
        if request:
            share_url = request.build_absolute_uri(f'/projects/shared/{obj.token}/')
        else:
            share_url = f"/projects/shared/{obj.token}/"
        subject = f"Shared Project: {obj.project.name}"
        body = f"I'd like to share this project with you:\n\n{obj.project.name}\n\nView it here: {share_url}"
        return f"mailto:?subject={quote(subject)}&body={quote(body)}"


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'project', 'user', 'user_name', 'user_email', 'message', 
                  'timestamp', 'updated_at']
        read_only_fields = ['id', 'timestamp', 'updated_at', 'user']


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Reminder
        fields = ['id', 'project', 'project_name', 'title', 'reminder_datetime', 
                  'status', 'status_display', 'created_at', 'updated_at', 
                  'created_by', 'created_by_name']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'created_by']

    def validate_reminder_datetime(self, value):
        """Ensure reminder datetime is in the future for new reminders"""
        from django.utils import timezone
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError("Reminder datetime must be in the future.")
        return value

