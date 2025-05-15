from rest_framework.serializers import ModelSerializer, SerializerMethodField
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate
import json

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'email_notification', 'average_rating', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data['avatar'] = instance.avatar
        return data

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(data.get('password'))
        u.save()
        return u

class EmployerSerializer(ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'user', 'name', 'tax_code', 'images', 'verified', 'location', 'coordinates']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.images:
            data['images'] = instance.images
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        return data

class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'employer_id', 'title', 'description', 'skills', 'salary', 'time_work', 'location', 'coordinates', 'status', 'work_hours', 'category_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        return data

class ApplySerializer(ModelSerializer):
    class Meta:
        model = Apply
        fields = ['id', 'candidate_id', 'job_id', 'status', 'applied_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['candidate'] = UserSerializer(instance.candidate_id.user).data if instance.candidate_id else None
        return data

class WorkScheduleSerializer(ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ['id', 'job_id', 'start_time', 'end_time', 'status']

class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'message', 'is_read', 'timestamp']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = UserSerializer(instance.sender).data
        data['receiver'] = UserSerializer(instance.receiver).data
        return data

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'notif_type', 'is_read', 'created_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data