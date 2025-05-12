from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from django.core.mail import send_mail
from django.conf import settings
from findJobApp.models import User, Company, Job, Application, WorkSchedule, ChatMessage, Notification
from findJobApp.serializers import UserSerializer, CompanySerializer, JobSerializer, ApplicationSerializer, WorkScheduleSerializer, ChatMessageSerializer, NotificationSerializer
from django.http import JsonResponse
import json

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        if request.method == "PATCH":
            u = request.user
            for k, v in request.data.items():
                if k in ['first_name', 'last_name']:
                    setattr(u, k, v)
                elif k == 'password':
                    u.set_password(v)
                elif k == 'email_notification':
                    u.email_notification = v
            u.save()
            return Response(UserSerializer(u).data)
        return Response(UserSerializer(request.user).data)

    @action(methods=['post'], url_path='send-email', detail=False, permission_classes=[permissions.IsAuthenticated])
    def send_email_notification(self, request):
        user = request.user
        if user.email_notification:
            subject = 'Job Application Update'
            message = f'Hello {user.username}, your application status has been updated.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            Notification.objects.create(user=user, message=message, notification_type='email')
            return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "Email notifications disabled"}, status=status.HTTP_400_BAD_REQUEST)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.filter(active=True)
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'], url_path='map-data', detail=True)
    def get_map_data(self, request, pk):
        company = self.get_object()
        if company.coordinates:
            coordinates = json.loads(company.coordinates) if isinstance(company.coordinates, str) else company.coordinates
            return Response({
                'location': company.location,
                'coordinates': coordinates,
                'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
            }, status=status.HTTP_200_OK)
        return Response({"message": "No map data available"}, status=status.HTTP_404_NOT_FOUND)

class JobViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Job.objects.filter(active=True)
    serializer_class = JobSerializer

    def get_queryset(self):
        query = self.queryset
        if self.action == 'list':
            q = self.request.query_params.get('q')
            if q:
                query = query.filter(title__icontains=q)
            location = self.request.query_params.get('location')
            if location:
                query = query.filter(location__icontains=location)
        return query

    @action(methods=['get'], url_path='company', detail=True)
    def get_company(self, request, pk):
        job = self.get_object()
        return Response(CompanySerializer(job.company).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='map-data', detail=True)
    def get_job_map_data(self, request, pk):
        job = self.get_object()
        if job.coordinates:
            coordinates = json.loads(job.coordinates) if isinstance(job.coordinates, str) else job.coordinates
            return Response({
                'location': job.location,
                'coordinates': coordinates,
                'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
            }, status=status.HTTP_200_OK)
        return Response({"message": "No map data available"}, status=status.HTTP_404_NOT_FOUND)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.filter(active=True)
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.filter(active=True)
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.filter(active=True)
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.filter(active=True)
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)