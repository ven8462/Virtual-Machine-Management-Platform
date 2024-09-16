from rest_framework import serializers
from .models import VirtualMachine, Backup, Snapshot, Payment, SubscriptionPlan, UserSubscription, AuditLog, CustomUser, Role
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import EmailValidator
from rest_framework.validators import UniqueValidator

class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            EmailValidator(message="Enter a valid email address."),
            UniqueValidator(queryset=CustomUser.objects.all(), message="Email is already taken.")
        ]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all(), message="Username is already taken.")]
    )
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(source='role.name', read_only=True)  # Include role in the response

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']  # Add role to fields

    def create(self, validated_data):
        # Set the default role if no role is provided
        default_role = Role.get_default_role()

        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=default_role  # Assign the default role
        )
        user.set_password(validated_data['password']) 
        user.save()

        # Generate both refresh and access tokens
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }

class VirtualMachineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMachine
        fields = ['name', 'status']  

    def validate_status(self, value):
        if value not in ['running', 'stopped']:
            raise serializers.ValidationError("Status must be either 'running' or 'stopped'.")
        return value


class VirtualMachineUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMachine
        fields = ['name', 'status'] 

    def validate_status(self, value):
        if value not in ['running', 'stopped']:
            raise serializers.ValidationError("Status must be either 'running' or 'stopped'.")
        return value


class VirtualMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMachine
        fields = '__all__'

class BackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = '__all__'

class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

