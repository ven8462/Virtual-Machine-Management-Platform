from rest_framework import viewsets, status
from .models import VirtualMachine, Backup, Snapshot, Payment, SubscriptionPlan, UserSubscription, AuditLog
from .serializers import VirtualMachineSerializer, BackupSerializer, SnapshotSerializer, PaymentSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, AuditLogSerializer, CustomUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VirtualMachineCreateSerializer



class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()
            return Response({
                "success": True,
                "message": "User created successfully",
                "refresh_token": user_data['refresh_token'],
                "access_token": user_data['access_token'],
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Invalid data",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access this endpoint

    def post(self, request):
        # Get username or email and password from request data
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        # Check if the username_or_email and password are provided
        if not username_or_email or not password:
            return Response({
                "success": False,
                "message": "Username/Email and password are required.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to find the user by username or email
        try:
            # If username_or_email contains '@', assume it's an email
            if '@' in username_or_email:
                user = CustomUser.objects.get(email=username_or_email)
            else:
                user = CustomUser.objects.get(username=username_or_email)

            # Validate password
            if not user.check_password(password):
                return Response({
                    "success": False,
                    "message": "Invalid username or password.",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # If the user is successfully authenticated, generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Login successful.",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "statusCode": 200
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid username or password.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

class CreateVirtualMachineView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        print(request.user)
        print(request.auth)
        serializer = VirtualMachineCreateSerializer(data=request.data)
        if serializer.is_valid():
            virtual_machine = serializer.save(owner=request.user)

            return Response({
                "success": True,
                "message": "Virtual machine created successfully.",
                "virtual_machine": {
                    "id": virtual_machine.id,
                    "name": virtual_machine.name,
                    "status": virtual_machine.status,
                    "owner": virtual_machine.owner.username,
                    "created_at": virtual_machine.created_at
                },
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


class UserVirtualMachinesView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user

        virtual_machines = VirtualMachine.objects.filter(owner=user)
        serializer = VirtualMachineSerializer(virtual_machines, many=True)
        return Response({
            "success": True,
            "message": "Virtual machines retrieved successfully.",
            "virtual_machines": serializer.data,
            "statusCode": 200
        }, status=status.HTTP_200_OK)


class VirtualMachineViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = VirtualMachine.objects.all()
    serializer_class = VirtualMachineSerializer

class BackupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer

class SnapshotViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
