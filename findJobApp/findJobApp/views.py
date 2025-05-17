from django.db.models.functions import Trunc
from keras.src.optimizers.schedules.learning_rate_schedule import serialize
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from django.core.mail import send_mail
from django.conf import settings
from sqlalchemy import True_, False_

from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate, Category, Follow
from findJobApp.serializers import UserSerializer, EmployerSerializer, JobSerializer, ApplySerializer, WorkScheduleSerializer, ChatMessageSerializer, NotificationSerializer, CandidateSerializer,EmployerRegisterSerializer,CandidateRegisterSerializer, CategorySerializer
from django.http import JsonResponse
import json
from .perms import IsAdminOrOwner, IsEmployerOwner


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrOwner]
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

    @action(methods=['post'],detail=False, url_path='register-employer',permission_classes=[permissions.AllowAny])
    def register_employer(self, request):
        serializer = EmployerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user= serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='register-candidate', permission_classes=[permissions.AllowAny])
    def register_candidate(self, request):
        serializer = CandidateRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

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

class EmployerViewSet(viewsets.ModelViewSet,generics.CreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    def get_permissions(self):
        if self.action in ['list']:
            return [permissions.IsAdminUser()]  # Chỉ cho admin hoặc superuser xem all employer
        return [permissions.IsAuthenticatedOrReadOnly()]  # Các action khác giữ nguyên

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

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Giữ kiểm tra login, cho phép đọc mà không cần đăng nhập

    def perform_create(self, serializer):
        employer = Employer.objects.get(user=self.request.user)
        serializer.save(employer_id=employer)
        followers = Follow.objects.filter(employer=employer)
        for f in followers:
            send_mail(
                subject='New Job Posted',
                message=f'Employer {employer.name} has posted a new job: {job.title}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[f.candidate.user.email],
                fail_silently=True,
            )

    def get_queryset(self): # tìm kiếm theo tên và vị trí và ngành nghề
        query = self.queryset
        if self.action == 'list':
            q = self.request.query_params.get('q')
            if q:
                query = query.filter(title__icontains=q)
            location = self.request.query_params.get('location')
            if location:
                query = query.filter(location__icontains=location)
            category_id = self.request.query_params.get('category_id')
            if category_id:
                query = query.filter(category_id=category_id)
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

    @action(methods=['get'], url_path='test-email', detail=False)
    def test_email(self, request):
        send_mail(
            subject='Test mail',
            message='test',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['tvloi250204@gmail.com'],
            fail_silently=False
        )
        return Response({'message': 'email sent successfully'})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CandidateViewSet(viewsets.ModelViewSet,generics.CreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ApplyViewSet(viewsets.ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySerializer

    def get_permissions(self):
        if self.action in ['approve', 'reject', 'job_applies']:
            return [permissions.IsAuthenticated(), IsEmployerOwner()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        candidate = Candidate.objects.get(user=self.request.user)
        serializer.save(candidate_id=candidate)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'candidate'):
            return Apply.objects.filer(candidate__user= user)
        elif hasattr(user, 'employer'):
            return Apply.objects.filer(job__employer_id__user=user)
        return Apply.objects.none()

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk = None):
        apply = self.get_object()
        apply.status = 'approved'
        apply.save()
        return Response({'status': 'Approved'})

    @action(detail=True, methods=['patch'], url_path='reject')
    def reject(self, request, pk=None):
        apply = self.get_object()
        apply.status='rejected'
        apply.save()
        return Response({'status':'Rejected'})

    @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[^/.]+)')
    def job_applies(self, request, job_id=None):
        applies =Apply.objects.filer(job__id = job_id, job__employer_id__user=request.user)
        serializer=self.get_serializer(applies, many=True)
        return Response(serializer.data)

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
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        return self.queryset.filter(user=self.request.user)