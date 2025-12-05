from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ShareLink, Project
from .serializers import ShareLinkSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_project(request, project_id):
    """Create or get share link for a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Verify ownership
    if project.created_by != request.user:
        return Response(
            {'error': 'You do not have permission to share this project.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if active share link exists
    existing_link = ShareLink.objects.filter(
        project=project, 
        is_active=True
    ).first()

    if existing_link:
        serializer = ShareLinkSerializer(existing_link, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create new share link
    share_link = ShareLink.objects.create(
        project=project,
        created_by=request.user
    )
    serializer = ShareLinkSerializer(share_link, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

