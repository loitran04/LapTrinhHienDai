from django.contrib import admin
from django.db.models import Count
from django.utils.html import mark_safe
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from findJobApp.models import User, Category, Job, Employer, Candidate, Apply, WorkSchedule, Review, Notification, Verification, Follow, ChatMessage

# Form tùy chỉnh để hỗ trợ CKEditor cho trường description
class JobForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Job
        fields = '__all__'

# Admin cho Employer
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tax_code', 'verified', 'location', 'coordinates']
    search_fields = ['name', 'tax_code']
    list_filter = ['verified']
    readonly_fields = ['image_view']

    @staticmethod
    def image_view(employer):
        first_image = employer.images.first()
        if first_image and first_image.image:
            return mark_safe(f"<img src='{first_image.image.url}' width='200' />")
        return "No Image"

# Admin cho Job
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'employer_id', 'category_id', 'status', 'work_hours', 'location', 'salary']
    search_fields = ['title', 'location', 'category_id__name']
    list_filter = ['status', 'employer_id', 'category_id']
    form = JobForm

# Admin cho Apply
class ApplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate_id', 'job_id', 'status', 'applied_date']
    search_fields = ['candidate_id__user__username', 'job_id__title']
    list_filter = ['status', 'applied_date']

# Admin cho WorkSchedule
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_id', 'start_time', 'end_time', 'status']
    search_fields = ['job_id__title']
    list_filter = ['status', 'start_time']

# Admin cho ChatMessage
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'message', 'timestamp', 'is_read']
    search_fields = ['sender__username', 'receiver__username', 'message']
    list_filter = ['is_read', 'timestamp']

# Admin cho Notification
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notif_type', 'is_read']
    search_fields = ['user__username', 'notif_type']
    list_filter = ['notif_type', 'is_read']

# Admin cho Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

# Admin cho Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'reviewer_id', 'reviewee_id', 'rating', 'comment', 'job_id']
    search_fields = ['reviewer_id__username', 'reviewee_id__username', 'job_id__title']
    list_filter = ['rating']

# Admin cho Verification
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'employer_id', 'document', 'verified_at']
    search_fields = ['employer_id__name']
    list_filter = ['verified_at']

# Admin cho Follow
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'employer_id', 'candidate_id', 'notify_email']
    search_fields = ['employer_id__name', 'candidate_id__user__username']

    def notify_email(self, obj):
        return obj.candidate_id.user.email if obj.candidate_id else None

    notify_email.short_description = 'Candidate Email'
# Admin cho Candidate
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'cv_link']
    search_fields = ['user__username']

# Admin cho User
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'email_notification', 'average_rating','role']
    search_fields = ['username', 'email']
    list_filter = ['email_notification']

# Admin site tùy chỉnh
class MyAdminSite(admin.AdminSite):
    site_header = 'findJobApp Admin'

    def get_urls(self):
        return [
            path('job-stats/', self.job_stats, name='job-stats'),
        ] + super().get_urls()

    @staticmethod
    def job_stats( request):
        job_stats = Job.objects.values('status').annotate(count=Count('id')).order_by('status')
        apply_stats = Apply.objects.values('applied_date__date').annotate(count=Count('id')).order_by('applied_date__date')
        employer_stats = Employer.objects.values('verified').annotate(count=Count('id')).order_by('verified')
        review_stats = Review.objects.values('rating').annotate(count=Count('id')).order_by('rating')
        return TemplateResponse(request, 'admin/job-stats.html', {
            'job_stats': list(job_stats),
            'apply_stats': list(apply_stats),
            'employer_stats': list(employer_stats),
            'review_stats': list(review_stats),
        })

# Khởi tạo admin site
admin_site = MyAdminSite(name='findJobApp')

# Đăng ký các mô hình vào admin
admin_site.register(User, UserAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Job, JobAdmin)
admin_site.register(Employer, EmployerAdmin)
admin_site.register(Candidate, CandidateAdmin)
admin_site.register(Apply, ApplyAdmin)
admin_site.register(WorkSchedule, WorkScheduleAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(Notification, NotificationAdmin)
admin_site.register(Verification, VerificationAdmin)
admin_site.register(Follow, FollowAdmin)
admin_site.register(ChatMessage, ChatMessageAdmin)