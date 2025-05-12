from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
import json

class User(AbstractUser):
    avatar = CloudinaryField(null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('employer', 'Employer'),
            ('candidate', 'Candidate')
        ],
        default='candidate'
    )
    email_notification = models.BooleanField(default=True)  # Để quản lý thông báo email

    def __str__(self):
        return self.username


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    images = CloudinaryField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255, null=True, blank=True)  # Địa điểm công ty (hỗ trợ Google Maps)
    coordinates = models.JSONField(null=True, blank=True)  # Lưu tọa độ (latitude, longitude) cho Google Maps

    def save(self, *args, **kwargs):
        # Đảm bảo coordinates là JSON hợp lệ
        if self.coordinates and isinstance(self.coordinates, dict):
            self.coordinates = json.dumps(self.coordinates)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = RichTextField()
    skills = models.TextField(null=True, blank=True)
    salary = models.CharField(max_length=100, null=True, blank=True)
    time_work = models.CharField(max_length=100, null=True, blank=True)  # Ca làm việc (ví dụ: "9:00-12:00")
    location = models.CharField(max_length=255, null=True, blank=True)  # Địa điểm làm việc
    coordinates = models.JSONField(null=True, blank=True)  # Tọa độ (hỗ trợ Google Maps)
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('closed', 'Closed'), ('draft', 'Draft')],
        default='draft'
    )
    work_hours = models.IntegerField(null=True, blank=True)  # Số giờ làm việc (hỗ trợ thống kê)

    def save(self, *args, **kwargs):
        # Đảm bảo coordinates là JSON hợp lệ
        if self.coordinates and isinstance(self.coordinates, dict):
            self.coordinates = json.dumps(self.coordinates)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Application(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    cv_link = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    applied_date = models.DateTimeField(auto_now_add=True)  # Ngày nộp đơn (hỗ trợ thống kê)


class Follow(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    notify_email = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'company')


class Review(BaseModel):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    role = models.CharField(
        max_length=20,
        choices=[('employer', 'Employer'), ('candidate', 'Candidate')]
    )
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)


class Verification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_link = models.URLField(null=True, blank=True)
    verified_by = models.CharField(max_length=255, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)


class WorkSchedule(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    start_time = models.DateTimeField()  # Thời gian bắt đầu ca
    end_time = models.DateTimeField()  # Thời gian kết thúc ca
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='scheduled'
    )

    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.start_time})"


class ChatMessage(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True)  # Liên kết với công việc (nếu có)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.message}"


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('system', 'System')],
        default='system'
    )
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"