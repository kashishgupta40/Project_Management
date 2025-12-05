from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    ShareLinkViewSet, CommentViewSet, ReminderViewSet, ProjectNoteViewSet
)
from .api_views import share_project

router = DefaultRouter()
router.register(r'share-links', ShareLinkViewSet, basename='sharelink')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'notes', ProjectNoteViewSet, basename='note')

urlpatterns = [
    path('projects/<uuid:project_id>/share/', share_project, name='api-share-project'),
    path('', include(router.urls)),
]

