from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate, Category, EmployerImage
import json

class UserSerializer(ModelSerializer):
    avatar = serializers.ImageField(required=False)
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

    # def create(self, validated_data):
    #     data = validated_data.copy()
    #     u = User(**data)
    #     u.set_password(data.get('password'))
    #     u.save()
    #     return u


class EmployerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerImage
        fields = ['id', 'image']


class EmployerSerializer(ModelSerializer):
    images = EmployerImageSerializer(many=True, read_only=True)
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
    # def create(self, validated_data):
    #     tax_code = validated_data.pop('tax_code')
    #     location = validated_data.pop('location')
    #     user = User.objects.create_user(**validated_data, role='employer')
    #     Employer.objects.create(user=user, name=user.username, tax_code=tax_code, location=location)
    #     return user
class EmployerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Employer
        fields = ['username', 'password', 'email', 'tax_code']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='employer'
        )
        employer = Employer.objects.create(user=user, **validated_data)
        return user



class CandidateSerializer(ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'user','name', 'cv_link']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data
    def create(self, validated_data):
        cv_link=validated_data.pop('cv_link')
        user=User.objects.create_user(**validated_data, role='candidate')
        Candidate.objects.create(user=user,name=user.username, cv_link=cv_link)


class CandidateRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Candidate
        fields = ['username', 'password', 'email', 'cv_link']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='candidate'
        )
        candidate = Candidate.objects.create(user=user, **validated_data)
        return user
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']
class JobSerializer(ModelSerializer):

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category',write_only=True
    )
    category = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'skills', 'salary', 'location', 'coordinates', 'status', 'work_hours', 'category','category_id']

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