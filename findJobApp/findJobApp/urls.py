from django.urls import path, include
from rest_framework.routers import DefaultRouter


from findJobApp.models import Candidate
from findJobApp.views import (UserViewSet, EmployerViewSet, JobViewSet, ApplyViewSet, WorkScheduleViewSet,
                              ChatMessageViewSet, NotificationViewSet, CandidateViewSet, CategoryViewSet, ReviewViewSet, stats_summary, GoogleLogin, FollowViewSet, VerificationViewSet)

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
router.register('reviews', ReviewViewSet, basename='reviews')
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'verifications', VerificationViewSet, basename='verifications')
urlpatterns = [
    path('', include(router.urls)),
    path('stats/summary/', stats_summary),
    path("auth/google/", GoogleLogin.as_view(), name="google_login"),
]