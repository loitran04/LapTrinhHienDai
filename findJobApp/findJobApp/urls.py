from django.urls import path, include
from rest_framework.routers import DefaultRouter

from findJobApp.models import Candidate
from findJobApp.views import UserViewSet, EmployerViewSet, JobViewSet, ApplyViewSet, WorkScheduleViewSet, ChatMessageViewSet, NotificationViewSet, CandidateViewSet, CategoryViewSet

# Cấu hình router cho các ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'employers', EmployerViewSet, basename='employer')
router.register(r'candidate', CandidateViewSet , basename='candidate')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'apply', ApplyViewSet, basename='apply')
router.register(r'work-schedules', WorkScheduleViewSet, basename='work-schedule')
router.register(r'chat-messages', ChatMessageViewSet, basename='chat-message')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]