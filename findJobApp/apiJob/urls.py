from findJobApp.admin import admin_site
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from findJobApp.views import UserViewSet, CompanyViewSet, JobViewSet, ApplicationViewSet, WorkScheduleViewSet, ChatMessageViewSet, NotificationViewSet

# Cấu hình router cho các ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'work-schedules', WorkScheduleViewSet, basename='work-schedule')
router.register(r'chat-messages', ChatMessageViewSet, basename='chat-message')
router.register(r'notifications', NotificationViewSet, basename='notification')

# Cấu hình Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="findJobApp API",
        default_version='v1',
        description="APIs for findJobApp - Hệ thống tìm kiếm việc làm",
        contact=openapi.Contact(email="2251052062loi@ou.edu.vn"),
        license=openapi.License(name="Trần Văn Lợi@2025"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),  # Bao gồm tất cả các endpoint từ router
    path('admin/', admin_site.urls),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]