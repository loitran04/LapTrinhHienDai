from rest_framework.serializers import ModelSerializer, SerializerMethodField
from findJobApp.models import User, Company, Job, Application, WorkSchedule, ChatMessage, Notification

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'role', 'email_notification']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            data['avatar'] = instance.avatar.url
        return data

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(data.get('password'))
        u.save()
        return u

class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'user', 'name', 'tax_code', 'description', 'images', 'verified', 'location', 'coordinates']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.images:
            data['images'] = instance.images.url
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        return data

class JobSerializer(ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'company', 'title', 'description', 'skills', 'salary', 'time_work', 'location', 'coordinates', 'status', 'work_hours']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        return data

class ApplicationSerializer(ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'user', 'job', 'cv_link', 'status', 'applied_date']

class WorkScheduleSerializer(ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ['id', 'user', 'job', 'start_time', 'end_time', 'status']

class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'job', 'message', 'is_read', 'created_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = UserSerializer(instance.sender).data
        data['receiver'] = UserSerializer(instance.receiver).data
        return data

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'notification_type', 'is_read', 'created_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data