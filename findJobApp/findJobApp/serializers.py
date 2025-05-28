from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
import re
import emoji
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate, Category, EmployerImage, Review, Verification
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

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        email = attrs.get('email', '')

        # --- Username ---
        if ' ' in username:
            raise serializers.ValidationError({"username": "Username không được chứa khoảng trắng."})
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError({"username": "Username không được chứa ký tự đặc biệt."})
        if emoji.emoji_count(username) > 0:
            raise serializers.ValidationError({"username": "Username không được chứa emoji."})
        if len(username) < 5:
            raise serializers.ValidationError({"username": "Username phải có ít nhất 5 ký tự."})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username đã tồn tại."})

        # --- Password ---
        if ' ' in password:
            raise serializers.ValidationError({"password": "Password không được chứa khoảng trắng."})
        if emoji.emoji_count(password) > 0:
            raise serializers.ValidationError({"password": "Password không được chứa emoji."})
        if len(password) < 6:
            raise serializers.ValidationError({"password": "Password phải có ít nhất 6 ký tự."})

        # --- Email ---
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email này đã được sử dụng."})

        return attrs

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
        return user


class CandidateRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Candidate
        fields = ['username', 'password', 'email', 'cv_link']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        email = attrs.get('email', '')
        cv_link = attrs.get('cv_link', '')

        # --- Username ---
        if ' ' in username:
            raise serializers.ValidationError({"username": "Username không được chứa khoảng trắng."})
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise serializers.ValidationError({"username": "Username không được chứa ký tự đặc biệt."})
        if emoji.emoji_count(username) > 0:
            raise serializers.ValidationError({"username": "Username không được chứa emoji."})
        if len(username) < 5:
            raise serializers.ValidationError({"username": "Username phải có ít nhất 5 ký tự."})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username đã tồn tại."})

        # --- Password ---
        if ' ' in password:
            raise serializers.ValidationError({"password": "Password không được chứa khoảng trắng."})
        if emoji.emoji_count(password) > 0:
            raise serializers.ValidationError({"password": "Password không được chứa emoji."})
        if len(password) < 6:
            raise serializers.ValidationError({"password": "Password phải có ít nhất 6 ký tự."})

        # --- Email ---
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email này đã được sử dụng."})

        if not re.match(r'^https?://', cv_link) or not cv_link.endswith(('.pdf', '.doc', '.docx')):
            raise serializers.ValidationError("CV phải là link hợp lệ và đúng định dạng.")

        return attrs
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

    def validate(self, attrs):
        if attrs.get("work_hours", 0) <= 0:
            raise serializers.ValidationError({"work_hours": "Số giờ làm phải lớn hơn 0."})
        if not attrs.get("salary", "").strip():
            raise serializers.ValidationError({"salary": "Lương không được để trống."})
        if not attrs.get("location", "").strip():
            raise serializers.ValidationError({"location": "Địa điểm không được để trống."})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        return data

class ApplySerializer(serializers.ModelSerializer):
    candidate = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Apply
        fields = ['id', 'job_id', 'cv_link', 'status', 'applied_date', 'candidate']
        read_only_fields = ['status', 'applied_date', 'candidate']

    def get_candidate(self, obj):
        if obj.candidate_id:
            return UserSerializer(obj.candidate_id.user).data
        return None

class WorkScheduleSerializer(ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ['id', 'job_id', 'start_time', 'end_time', 'status']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError("Giờ bắt đầu phải trước giờ kết thúc.")
        return attrs
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
def contains_dangerous_tags(text):
    """
    Kiểm tra xem văn bản có chứa các thẻ HTML nguy hiểm (XSS) hay không.
    """
    return bool(re.search(r'<\s*(script|iframe|embed|object|link|style)[^>]*>', text, re.IGNORECASE))

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewee', 'job', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer', 'created_at']

    def validate(self, attrs):
        reviewer = self.context['request'].user  # reviewer luôn là người gửi request
        reviewee = attrs.get('reviewee')
        job = attrs.get('job')
        rating = attrs.get('rating')
        comment = attrs.get('comment', '').strip()

        # Công việc phải ở trạng thái 'completed'
        if job.status != 'completed':
            raise serializers.ValidationError({"job": "Công việc chưa hoàn thành."})

        # Không được tự đánh giá bản thân
        if reviewer == reviewee:
            raise serializers.ValidationError({"reviewee": "Không thể tự đánh giá chính mình."})

        # Không được đánh giá trùng
        if Review.objects.filter(reviewer=reviewer, reviewee=reviewee, job=job).exists():
            raise serializers.ValidationError("Bạn đã đánh giá người này cho công việc này rồi.")

        # Validate rating
        if not (1 <= rating <= 5):
            raise serializers.ValidationError({"rating": "Đánh giá phải từ 1 đến 5 sao."})

        # Validate comment
        if not comment:
            raise serializers.ValidationError({"comment": "Bình luận không được để trống."})
        if len(comment) > 1000:
            raise serializers.ValidationError({"comment": "Bình luận không được vượt quá 1000 ký tự."})
        if contains_dangerous_tags(comment):
            raise serializers.ValidationError({"comment": "Bình luận chứa mã độc hoặc thẻ HTML không an toàn."})

        attrs['comment']=comment
        return attrs

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = ['id', 'employer', 'document', 'verified_at', 'is_verified']
        read_only_fields = ['verified_at', 'is_verified', 'employer']