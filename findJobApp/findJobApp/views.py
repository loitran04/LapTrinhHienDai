from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from django.core.mail import send_mail
from django.conf import settings
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification
from findJobApp.serializers import UserSerializer, EmployerSerializer, JobSerializer, ApplySerializer, WorkScheduleSerializer, ChatMessageSerializer, NotificationSerializer
from django.http import JsonResponse
import json

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Giữ kiểm tra login, cho phép đọc mà không cần đăng nhập

    @action(methods=['get', 'patch'], url_path='current-user', detail=False, permission_classes=[permissions.IsAuthenticated])  # Chỉ người dùng đã đăng nhập
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

    @action(methods=['post'], url_path='send-email', detail=False, permission_classes=[permissions.IsAuthenticated])  # Chỉ người dùng đã đăng nhập
    def send_email_notification(self, request):
        user = request.user
        if user.email_notification:
            subject = 'Job Application Update'
            message = f'Hello {user.username}, your application status has been updated.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            Notification.objects.create(user=user, notif_type='email', is_read=False)
            return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "Email notifications disabled"}, status=status.HTTP_400_BAD_REQUEST)

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Giữ kiểm tra login, cho phép đọc mà không cần đăng nhập

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'], url_path='map-data', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])  # Có thể đọc mà không cần đăng nhập
    def get_map_data(self, request, pk):
        employer = self.get_object()
        if employer.coordinates:
            coordinates = json.loads(employer.coordinates) if isinstance(employer.coordinates, str) else employer.coordinates
            return Response({
                'location': employer.location,
                'coordinates': coordinates,
                'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
            }, status=status.HTTP_200_OK)
        return Response({"message": "No map data available"}, status=status.HTTP_404_NOT_FOUND)

class JobViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Giữ kiểm tra login, cho phép đọc mà không cần đăng nhập

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

    @action(methods=['get'], url_path='employer', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])  # Có thể đọc mà không cần đăng nhập
    def get_employer(self, request, pk):
        job = self.get_object()
        return Response(EmployerSerializer(job.employer_id).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='map-data', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])  # Có thể đọc mà không cần đăng nhập
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

class ApplyViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def perform_create(self, serializer):
        candidate = Candidate.objects.get(user=self.request.user)
        serializer.save(candidate_id=candidate)

class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Cần điều chỉnh logic, xem ghi chú bên dưới

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)