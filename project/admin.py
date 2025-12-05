from django.contrib import admin
from .models import Project, ProjectFile, ProjectNote, ShareLink, Comment, Reminder


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'start_date', 'end_date', 'created_at']
    list_filter = ['created_at', 'start_date', 'end_date']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'attachment']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ['project', 'content_preview', 'created_at']
    list_filter = ['created_at', 'project']
    search_fields = ['content']
    readonly_fields = ['id', 'created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ['project', 'token_short', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['token', 'project__name']
    readonly_fields = ['id', 'token', 'created_at']

    def token_short(self, obj):
        return f"{obj.token[:16]}..." if obj.token else "-"
    token_short.short_description = 'Token'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'message_preview', 'timestamp']
    list_filter = ['timestamp', 'project']
    search_fields = ['message', 'user__name', 'user__email']
    readonly_fields = ['id', 'timestamp', 'updated_at']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'reminder_datetime', 'status', 'created_by']
    list_filter = ['status', 'reminder_datetime', 'project']
    search_fields = ['title', 'project__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
