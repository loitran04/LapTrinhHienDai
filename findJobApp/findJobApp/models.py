from django.db import models
from django.contrib.auth.models import AbstractUser

# Định nghĩa các lựa chọn cho enum
STATUS_APP_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

STATUS_JOB_CHOICES = [
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('draft', 'Draft'),
]

STATUS_WORK_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
]

# Mô hình User (kế thừa từ AbstractUser)
class User(AbstractUser):
    avatar = models.CharField(max_length=255, blank=True, null=True)
    email_notification = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0.0)

# Mô hình Category
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Mô hình Job
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.TextField()
    salary = models.CharField(max_length=50)
    time_work = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_JOB_CHOICES, default='draft')
    work_hours = models.IntegerField()
    employer_id = models.ForeignKey('Employer', on_delete=models.CASCADE)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# Mô hình Employer
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50)
    images = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

# Mô hình Candidate
class Candidate(models.Model):
    cv_link = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Mô hình Apply
class Apply(models.Model):
    status = models.CharField(max_length=10, choices=STATUS_APP_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)

# Mô hình WorkSchedule
class WorkSchedule(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_WORK_CHOICES, default='scheduled')
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)

# Mô hình Review
class Review(models.Model):
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewer')
    reviewee_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewee')
    rating = models.IntegerField()
    comment = models.TextField()
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)

# Mô hình Notification
class Notification(models.Model):
    notif_type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# Mô hình Verification
class Verification(models.Model):
    employer_id = models.ForeignKey(Employer, on_delete=models.CASCADE)
    document_link = models.CharField(max_length=255)
    verified_at = models.DateTimeField(null=True, blank=True)

# Mô hình Follow
class Follow(models.Model):
    notify_email = models.BooleanField(default=True)
    employer_id = models.ForeignKey(Employer, on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)

# Mô hình ChatMessage
class ChatMessage(models.Model):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')

# Mô hình Admin
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)