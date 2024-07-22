from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('account.urls')),
    path('projects/', include('project.urls')),
    path('projects/<uuid:project_id>/', include('todolist.urls')),
    path('projects/<uuid:project_id>/<uuid:todolist_id>/', include('task.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
