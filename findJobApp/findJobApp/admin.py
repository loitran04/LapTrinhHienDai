from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.urls import path
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from findJobApp.models import User, Company, Job, Application, WorkSchedule, ChatMessage, Notification

# Form tùy chỉnh để hỗ trợ CKEditor cho các trường RichTextField
class JobForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Job
        fields = '__all__'

class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tax_code', 'verified', 'location']
    search_fields = ['name', 'tax_code']
    list_filter = ['verified']
    readonly_fields = ['image_view']

    @staticmethod
    def image_view(company):
        if company.images:
            return mark_safe(f"<img src='{company.images.url}' width='200' />")
        return "No Image"

class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'company', 'status', 'time_work', 'location']
    search_fields = ['title', 'location']
    list_filter = ['status', 'company']
    form = JobForm

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'job', 'status', 'applied_date']
    search_fields = ['user__username', 'job__title']
    list_filter = ['status', 'applied_date']

class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'job', 'start_time', 'end_time', 'status']
    search_fields = ['user__username', 'job__title']
    list_filter = ['status', 'start_time']

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'message', 'created_date', 'is_read']
    search_fields = ['sender__username', 'receiver__username', 'message']
    list_filter = ['is_read', 'created_date']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'notification_type', 'is_read', 'created_date']
    search_fields = ['user__username', 'message']
    list_filter = ['notification_type', 'is_read', 'created_date']

class MyAdminSite(admin.AdminSite):
    site_header = 'findJobApp Admin'

    def get_urls(self):
        return [
            path('job-stats/', self.job_stats, name='job-stats'),
        ] + super().get_urls()

    def job_stats(self, request):
        # Thống kê số lượng công việc theo trạng thái
        job_stats = Job.objects.values('status').annotate(count=Count('id')).order_by('status')
        # Thống kê số lượng ứng tuyển theo ngày
        application_stats = Application.objects.values('applied_date__date').annotate(count=Count('id')).order_by('applied_date__date')
        return TemplateResponse(request, 'admin/job-stats.html', {
            'job_stats': list(job_stats),
            'application_stats': list(application_stats),
        })

# Khởi tạo admin site
admin_site = MyAdminSite(name='findJobApp')

# Đăng ký các mô hình vào admin
admin_site.register(User)
admin_site.register(Company, CompanyAdmin)
admin_site.register(Job, JobAdmin)
admin_site.register(Application, ApplicationAdmin)
admin_site.register(WorkSchedule, WorkScheduleAdmin)
admin_site.register(ChatMessage, ChatMessageAdmin)
admin_site.register(Notification, NotificationAdmin)