from rest_framework import viewsets, status
from .models import VirtualMachine, Backup, Snapshot, Payment, SubscriptionPlan, UserSubscription, AuditLog,CustomUser, Role
from .serializers import VirtualMachineSerializer, VirtualMachineUpdateSerializer, BackupSerializer, SnapshotSerializer, PaymentSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, AuditLogSerializer, CustomUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VirtualMachineCreateSerializer, BackupCreateSerializer
from django.shortcuts import get_object_or_404


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
        user = request.user
        
        # Check if the user has an admin role
        if user.role.name != 'Admin':
            return Response({
                "success": False,
                "message": "Permission denied. You don't have rights to perform this action.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = VirtualMachineCreateSerializer(data=request.data)
        if serializer.is_valid():
            virtual_machine = serializer.save(owner=user)

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


class UpdateVirtualMachineView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, vm_id):
        user = request.user
        
        # Check if the user has an admin role
        if user.role.name != 'Admin':
            return Response({
                "success": False,
                "message": "Permission denied. You don't have rights to perform this action.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)
        

        try:
            virtual_machine = VirtualMachine.objects.get(id=vm_id, owner=request.user)
        except VirtualMachine.DoesNotExist:
            return Response({
                "success": False,
                "message": "Virtual machine not found or not owned by the user.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = VirtualMachineUpdateSerializer(virtual_machine, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Virtual machine updated successfully.",
                "virtual_machine": serializer.data,
                "statusCode": 200
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteVirtualMachineView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, vm_id):
        user = request.user
        
        if user.role.name != 'Admin':
            return Response({
                "success": False,
                "message": "Permission denied. You don't have rights to perform this action.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        virtual_machine = get_object_or_404(VirtualMachine, id=vm_id)

        if virtual_machine.owner != user:
            return Response({
                "success": False,
                "message": "You do not have permission to delete this virtual machine.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        virtual_machine.delete()

        AuditLog.objects.create(
            user=user,
            action='vm_deleted',
            description=f"Virtual machine '{virtual_machine.name}' was deleted."
        )

        return Response({
            "success": True,
            "message": "Virtual machine deleted successfully.",
            "statusCode": 204
        }, status=status.HTTP_204_NO_CONTENT)


class CreateBackupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Check if the user has the 'Standard User' role
        if user.role.name != 'Standard User':
            return Response({
                "success": False,
                "message": "Permission denied. Only Standard Users can create backups.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = BackupCreateSerializer(data=request.data)
        if serializer.is_valid():
            backup = serializer.save()
            return Response({
                "success": True,
                "message": "Backup created successfully.",
                "backup": {
                    "id": backup.id,
                    "vm": backup.vm.id,
                    "size": backup.size,
                    "created_at": backup.created_at
                },
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


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
