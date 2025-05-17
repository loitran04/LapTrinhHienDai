from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

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
ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('candidate', 'Candidate'),
]

# Mô hình User (kế thừa từ AbstractUser)
class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email_notification = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0.0)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='candidate')


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
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_JOB_CHOICES, default='draft')
    work_hours = models.IntegerField()
    employer_id = models.ForeignKey('Employer', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jobs')
    def __str__(self):
        return self.title

# Mô hình Employer
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    name = models.CharField(max_length=255)
    tax_code = models.CharField(max_length=50)
    verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
class EmployerImage(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='employer_images/')
    uploaded_at= models.DateTimeField(auto_now_add=True)
# Mô hình Candidate
class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    name = models.CharField(max_length=255)
    cv_link = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.name

# Mô hình Apply
class Apply(models.Model):
    status = models.CharField(max_length=10, choices=STATUS_APP_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    cv_link = models.URLField()

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
    created_date = models.DateTimeField(auto_now_add=True)

# Mô hình Verification
class Verification(models.Model):
    employer_id = models.ForeignKey(Employer, on_delete=models.CASCADE)
    document_link = models.CharField(max_length=255)
    verified_at = models.DateTimeField(null=True, blank=True)

# Mô hình Follow
class Follow(models.Model):
    employer_id = models.ForeignKey(Employer, on_delete=models.CASCADE)
    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate_id', 'employer_id')
# Mô hình ChatMessage
class ChatMessage(models.Model):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')

# @receiver(post_save, sender=User)
# def create_profile_for_role(sender, instance, created, **kwargs):
#     if created:
#         if instance.role == 'employer':
#             Employer.objects.create(user=instance, name=instance.username, tax_code="", location="")
#         elif instance.role=='candidate':
#             Candidate.objects.create(user=instance)
