from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import viewsets, generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status as http_status
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate, Category, Follow, Review, Verification, Follow
from findJobApp.serializers import (UserSerializer, EmployerSerializer, JobSerializer, ApplySerializer,
                                    WorkScheduleSerializer, ChatMessageSerializer, NotificationSerializer, CandidateSerializer,EmployerRegisterSerializer,CandidateRegisterSerializer,
                                    CategorySerializer, ReviewSerializer, VerificationSerializer, FollowSerializer)
from django.http import JsonResponse
import json
from .perms import IsAdminOrOwner, IsEmployerOwner
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

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

    @action(methods=['post'], detail=False, url_path='register-employer', permission_classes=[permissions.AllowAny])
    def register_employer(self, request):
        serializer = EmployerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employer = serializer.save()  # Lưu và lấy đối tượng Employer
        user = employer.user  # Lấy đối tượng User liên kết
        return Response(serializer.to_representation(employer), status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='register-candidate', permission_classes=[permissions.AllowAny])
    def register_candidate(self, request):
        serializer = CandidateRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.to_representation(user), status=status.HTTP_201_CREATED)

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

    @action(methods=['get'], url_path='map-data', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])
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

    @action(methods=['get'], detail=False, url_path='current-employer')
    def current_employer(self, request):
        user = request.user
        try:
            employer = user.employer_profile  # related_name='employer_profile'
        except Employer.DoesNotExist:
            return Response({"detail": "User is not an employer."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(employer)
        return Response(serializer.data)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Giữ kiểm tra login, cho phép đọc mà không cần đăng nhập

    def perform_create(self, serializer):
        employer = self.request.user.employer_profile

        if not employer.verified:
            raise PermissionDenied("Tai khoan chua xac thuc!")

        followers = Follow.objects.filter(employer_id=employer)
        job = serializer.save(employer_id=employer)
        for f in followers:
            send_mail(
                subject='New Job Posted',
                message=f'Employer {employer.name} has posted a new job: {job.title}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[f.candidate_id.user.email],
                fail_silently=True,
            )

    def get_queryset(self):
        query = Job.objects.all()  # <-- lấy toàn bộ dữ liệu gốc
        print(">> SQL:", query.query)
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
            salary = self.request.query_params.get('salary')
            if salary:
                query = query.filter(salary__icontains=salary)
            work_hours = self.request.query_params.get('work_hours')
            if work_hours:
                query = query.filter(work_hours=work_hours)
        return query


    @action(methods=['get'], url_path='employer', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])  # Có thể đọc mà không cần đăng nhập
    def get_employer(self, request, pk):
        job = self.get_object()
        return Response(EmployerSerializer(job.employer_id).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='map-data', detail=True, permission_classes=[permissions.IsAuthenticatedOrReadOnly])
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

    @action(methods=['get'], detail=False, url_path='current-candidate')
    def current_candidate(self, request):
        user = request.user
        try:
            candidate = user.candidate_profile  # related_name='candidate_profile'
        except Candidate.DoesNotExist:
            return Response({"detail": "User is not a candidate."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(candidate)
        return Response(serializer.data)
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
        if hasattr(user, 'candidate_profile'):
            return Apply.objects.filter(candidate_id=user.candidate_profile)
        elif hasattr(user, 'employer_profile'):
            return Apply.objects.filter(job_id__employer_id__user=user)
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
        user = request.user
        employer = user.employer_profile
        applies = Apply.objects.filter(job_id__id=job_id, job_id__employer_id=employer)
        serializer = self.get_serializer(applies, many=True)
        return Response(serializer.data)

class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['post'], detail=True, url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        schedule = self.get_object()
        if schedule.job.employer.user == request.user and schedule.status == 'scheduled':
            schedule.status='completed'
            schedule.job.status = 'closed'
        schedule.save()
        schedule.job.save()
        return Response({"detail": "Lịch làm việc đã được đánh dấu là hoàn thành."},status =http_status.HTTP_200_OK)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        return self.queryset.filter(user=self.request.user)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        reviewee = self.request.query_params.get('reviewee')
        if reviewee:
            queryset = queryset.filter(reviewee=reviewee)
        job = self.request.query_params.get('job')
        if job:
            queryset = queryset.filter(job=job)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
@api_view(['GET'])
def stats_summary(request):
    from_date = request.GET.get('from', '2025-01-01')
    to_date = request.GET.get('to', '2025-12-31')

    from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
    to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

    jobs = Job.objects.filter(created_at__range=(from_date, to_date))\
                .annotate(month=TruncMonth('created_at'))\
                .values('month')\
                .annotate(total=Count('id'))

    candidates = Candidate.objects.filter(user__date_joined__range=(from_date, to_date))\
                .annotate(month=TruncMonth('user__date_joined'))\
                .values('month')\
                .annotate(total=Count('id'))

    employers = Employer.objects.filter(user__date_joined__range=(from_date, to_date))\
                .annotate(month=TruncMonth('user__date_joined'))\
                .values('month')\
                .annotate(total=Count('id'))

    def convert(data):
        return {item['month'].strftime('%Y-%m'): item['total'] for item in data}

    return Response({
        "jobs_created": convert(jobs),
        "candidates_registered": convert(candidates),
        "employers_registered": convert(employers),
    })


class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            employer = Employer.objects.get(user=self.request.user)
        except Employer.DoesNotExist:
            raise PermissionDenied("Chỉ nhà tuyển dụng mới được xác minh.")

        serializer.save(employer=employer)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            raise PermissionDenied("Chỉ admin được quyền xét duyệt.")

        instance = self.get_object()
        is_verified = request.data.get("is_verified", False)

        if is_verified:
            instance.is_verified = True
            instance.verified_at = timezone.now()
            instance.save()
            instance.employer.verified = True
            instance.employer.save()

        return Response(self.get_serializer(instance).data)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Verification.objects.filter(is_verified=False)
        return Verification.objects.none()

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        candidate = request.user.candidate_profile
        follows = Follow.objects.filter(candidate_id=candidate)
        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data)

    def create(self, request):
        candidate = request.user.candidate_profile
        employer_id = request.data.get('employer_id')

        try:
            employer = Employer.objects.get(id=employer_id)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(candidate_id=candidate, employer_id=employer)
        if not created:
            return Response({'message': 'Đã theo dõi rồi'}, status=status.HTTP_200_OK)

        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=False)
    def unfollow(self, request):
        candidate = request.user.candidate_profile
        employer_id = request.query_params.get('employer_id')

        deleted, _ = Follow.objects.filter(candidate_id=candidate, employer_id_id=employer_id).delete()
        if deleted:
            return Response({'message': 'Đã bỏ theo dõi'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Không tìm thấy'}, status=status.HTTP_400_BAD_REQUEST)