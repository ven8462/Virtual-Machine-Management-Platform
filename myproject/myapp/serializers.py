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


class BackupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = ['vm', 'size']

    def validate_vm(self, value):
        if not VirtualMachine.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The specified virtual machine does not exist.")
        return value

    def validate_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("Backup size must be greater than zero.")
        return value


class MoveVirtualMachineSerializer(serializers.ModelSerializer):
    new_owner = serializers.CharField()

    class Meta:
        model = VirtualMachine
        fields = ['new_owner']

    def validate_new_owner(self, value):
        try:
            new_owner = CustomUser.objects.get(username=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("The specified user does not exist.")

        # Ensure that the new owner has the 'Standard User' role
        if new_owner.role.name != 'Standard User':
            raise serializers.ValidationError("The new owner must be a Standard User.")
        
        return new_owner


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'max_vms', 'max_backups', 'cost']

class BillingSerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer()
    
    class Meta:
        model = Payment
        fields = ['amount', 'created_at', 'status', 'subscription_plan']  

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'cost', 'duration']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['user', 'subscription_plan', 'started_at', 'expires_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['user', 'amount', 'status', 'transaction_id', 'created_at']



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

