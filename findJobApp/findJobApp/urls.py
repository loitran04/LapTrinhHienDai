from django.urls import path, include
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

urlpatterns = [
    path('', include(router.urls)),
]