from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
import re
import emoji
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from findJobApp.models import User, Employer, Job, Apply, WorkSchedule, ChatMessage, Notification, Candidate, Category, EmployerImage, Review, Verification, Follow
import json

class UserSerializer(ModelSerializer):
    avatar = serializers.ImageField(required=False)
    # role = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'email_notification', 'average_rating', 'password','role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # def get_role(self, user):
    #     if hasattr(user, 'employer_profile'):
    #         return 'employer'
    #     elif hasattr(user, 'candidate_profile'):
    #         return 'candidate'
    #     elif hasattr(user, 'admin'):
    #         return 'admin'
    #     return 'unknown'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = instance.avatar.url if instance.avatar else ''
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
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else ''
        return data


class EmployerSerializer(ModelSerializer):
    images = EmployerImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Employer
        fields = [
            'id', 'user', 'name', 'avatar', 'tax_code', 'images',
            'uploaded_images', 'verified', 'location', 'coordinates'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Xóa phần gán lại images vì đã được xử lý tự động bởi EmployerImageSerializer
        # if instance.images:
        #     data['images'] = instance.images  # Dòng này gây lỗi, hãy xóa nó

        # Xử lý coordinates
        if instance.coordinates:
            data['coordinates'] = json.loads(instance.coordinates) if isinstance(instance.coordinates, str) else instance.coordinates
        data['avatar'] = instance.avatar.url if instance.avatar else ''
        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        avatar = validated_data.pop('avatar', None)
        employer = Employer.objects.create(**validated_data, avatar=avatar)
        for image in uploaded_images:
            EmployerImage.objects.create(employer=employer, image=image)
        return employer

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Nếu muốn cập nhật ảnh mới mà không xóa ảnh cũ
        for image in uploaded_images:
            EmployerImage.objects.create(employer=instance, image=image)

        return instance
class EmployerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    avatar = serializers.ImageField(required=False, allow_null=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )


    class Meta:
        model = Employer
        fields = ['username', 'password','name', 'email', 'tax_code', 'avatar', 'images', 'location']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        email = attrs.get('email', '')
        avatar = attrs.get('avatar', None)
        images = attrs.get('images', [])
        location = attrs.get('location', '').strip()

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
        # --- Avatar ---
        if not avatar:
            raise serializers.ValidationError({"avatar": "Bạn phải cung cấp avatar."})

        # --- Images ---
        if not images or len(images) < 3:
            raise serializers.ValidationError({"images": "Bạn phải cung cấp ít nhất 3 ảnh công ty."})
        if not location:
            raise serializers.ValidationError({"location": "Bạn phải nhập địa chỉ công ty."})

        return attrs

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        avatar = validated_data.pop('avatar', None)
        images = validated_data.pop('images', [])

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='employer',
            avatar=avatar
        )
        employer = Employer.objects.create(user=user, avatar=avatar, **validated_data)
        # Tạo EmployerImage nếu có danh sách ảnh
        for img in images:
            EmployerImage.objects.create(employer=employer, image=img)
        return employer

    def to_representation(self, instance):
        user = instance.user
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": instance.name,  # ✅ trả về tên công ty
            "avatar": instance.avatar.url if instance.avatar else '',
            "email_notification": user.email_notification,
            "average_rating": user.average_rating,
            "role": user.role,
            "tax_code": instance.tax_code,
            "location": instance.location  # ✅ Thêm dòng này
        }


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
    avatar = serializers.ImageField(required=True)  # phải có để lưu avatar
    name = serializers.CharField(required=True)

    class Meta:
        model = Candidate
        fields = ['username', 'password','name', 'email', 'cv_link','avatar']

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
        name = validated_data.pop('name')
        avatar = validated_data.get('avatar')
        cv_link = validated_data.pop('cv_link')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='candidate',
            avatar = avatar
        )
        Candidate.objects.create(user=user, name=name, avatar=avatar, cv_link=cv_link)
        return user

    def to_representation(self, instance):
        try:
            candidate = Candidate.objects.get(user=instance)
            avatar = candidate.avatar.url if candidate.avatar else ''
            name = candidate.name
            cv_link = candidate.cv_link
        except Candidate.DoesNotExist:
            avatar = ''
            name = ''
            cv_link = ''

        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'name': name,
            'avatar': avatar,
            'email_notification': instance.email_notification,
            'average_rating': instance.average_rating,
            'role': instance.role,
            'cv_link': cv_link
        }
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']
def is_valid_currency_format(value):
    # Ví dụ: 1.000 hoặc 123.456.789
    pattern = r'^\d{1,3}(\.\d{3})*$'
    return bool(re.fullmatch(pattern, value))
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
        salary = attrs.get("salary", "").strip()
        if not salary:
            raise serializers.ValidationError({"salary": "Lương không được để trống."})
            # ✅ Kiểm tra định dạng tiền tệ Việt Nam (ví dụ: 1.000, 10.000.000)
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
    def validate(self, attrs):
        requests = self.context.get('request')
        candidate = requests.user.candidate_profile

        job = attrs.get('job_id')
        if Apply.objects.filter(job_id=job, candidate_id=candidate).exists():
            raise serializers.ValidationError("Ban da ung tuyen roi!")
        return attrs
    def create(self, validated_data):
        candidate = self.context['request'].user.candidate_profile
        return Apply.objects.create(candidate_id=candidate, **validated_data)
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'employer_id', 'followed_at']
        read_only_fields = ['id', 'followed_at']
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