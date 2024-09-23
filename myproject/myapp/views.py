from rest_framework import viewsets, status, generics
from .models import VirtualMachine, Backup, UserAssignedVM, Snapshot, Payment, SubscriptionPlan, UserSubscription, AuditLog,CustomUser, Role
from .serializers import VirtualMachineSerializer, MoveVirtualMachineSerializer, VirtualMachineUpdateSerializer, BackupSerializer, SnapshotSerializer, PaymentSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, AuditLogSerializer, CustomUserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import VirtualMachineCreateSerializer, BackupCreateSerializer, BillingSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .serializers import AssignVMMachineSerializer
from .models import SubUser
from .serializers import SubUserSerializer, BackupSerializer
from .serializers import VirtualMachineSerializers
from .serializers import PaymentSerializer
from django.contrib.auth import get_user_model
import jwt
import google.auth.transport.requests
import google.oauth2.id_token
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from django.core.mail import send_mail

# Load environment variables from .env
load_dotenv()


User = get_user_model()

import requests


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        google_token = request.data.get('google_token')

        if google_token:
            user_info = self.verify_google_token(google_token)
            if not user_info:
                return Response({
                    "success": False,
                    "message": "Invalid Google token.",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create or get the user
            user, created = CustomUser.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info['email'].split('@')[0],  
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                }
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "User created successfully" if created else "User already exists",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)

        # Fallback to regular sign-up
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()
            refresh = RefreshToken.for_user(user_data)
            return Response({
                "success": True,
                "message": "User created successfully",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Invalid data",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)

    def verify_google_token(self, token):
        """ Verify the Google token and get user info """
        client_id = "132929471498-lcfm9oobe5paa6re1bdvu34ac6m13t6a.apps.googleusercontent.com"
        response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')

        if response.status_code == 200:
            return response.json()  
        return None



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_type = request.data.get('login_type', 'manual')  # "manual" or "google"
        
        if login_type == 'manual':
            return self.manual_login(request)
        elif login_type == 'google':
            return self.google_login(request)
        else:
            return Response({
                "success": False,
                "message": "Invalid login type.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

    def manual_login(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if not username_or_email or not password:
            return Response({
                "success": False,
                "message": "Username/Email and password are required.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the user exists by email or username
            if '@' in username_or_email:
                user = CustomUser.objects.get(email=username_or_email)
            else:
                user = CustomUser.objects.get(username=username_or_email)

            if not user.check_password(password):
                return Response({
                    "success": False,
                    "message": "Invalid username or password.",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Login successful.",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "role": user.role.name,  # Return user's role
                "statusCode": 200
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid username or password.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

    def google_login(self, request):
        id_token = request.data.get('id_token')

        if not id_token:
            return Response({
                "success": False,
                "message": "Google ID token is required.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token using Google's services
            request_obj = google.auth.transport.requests.Request()
            id_info = google.oauth2.id_token.verify_oauth2_token(
                id_token, request_obj, settings.GOOGLE_CLIENT_ID
            )

            if 'email' not in id_info:
                return Response({
                    "success": False,
                    "message": "Invalid Google token.",
                    "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

            email = id_info['email']

            # Check if the user already exists
            user, created = CustomUser.objects.get_or_create(email=email, defaults={
                'username': email.split('@')[0],  # Set username as part of the email before @
                'password': CustomUser.objects.make_random_password(),  # Create random password
            })

            if created:
                # Assign any default role or additional info for newly created users
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Google login successful.",
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "role": user.role.name,
                "statusCode": 200
            }, status=status.HTTP_200_OK)

        except ValueError as ve:
            # Invalid token
            return Response({
                "success": False,
                "message": "Invalid Google ID token.",
                "error": str(ve),
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)


class CreateVirtualMachineView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Check if the user has a Standard User role
        if user.role.name != 'Standard User':
            return Response({
                "success": False,
                "message": "Permission denied. You don't have rights to perform this action.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = VirtualMachineCreateSerializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                virtual_machine = serializer.save(owner=user)

                return Response({
                    "success": True,
                    "message": "Virtual machine created successfully.",
                    "virtual_machine": {
                        "id": virtual_machine.id,
                        "name": virtual_machine.name,
                        "status": virtual_machine.status,
                        "cpu": virtual_machine.cpu,
                        "ram": virtual_machine.ram,
                        "cost": virtual_machine.cost,
                        "owner": virtual_machine.owner.username,
                        "created_at": virtual_machine.created_at
                    },
                    "statusCode": 201
                }, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({
                "success": False,
                "message": "Validation error.",
                "errors": ve.detail,  # Return detailed validation error
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "success": False,
                "message": "An error occurred while creating the virtual machine.",
                "error": str(e),  # Log the exception
                "statusCode": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllVirtualMachinesView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        # Fetch all virtual machines, not limited to the current user
        virtual_machines = VirtualMachine.objects.all()
        serializer = VirtualMachineSerializer(virtual_machines, many=True)
        return Response({
            "success": True,
            "message": "All virtual machines retrieved successfully.",
            "virtual_machines": serializer.data,
            "statusCode": 200
        }, status=status.HTTP_200_OK)



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




class AssignVMMachineView(APIView):
    def put(self, request, *args, **kwargs):
        serializer = AssignVMMachineSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            vm_id = serializer.validated_data['vm_id']

            try:
                # Fetch the user and the VM
                user = CustomUser.objects.get(pk=user_id)
                vm = VirtualMachine.objects.get(pk=vm_id)

                # Assign the VM to the user and save the assignment
                vm.owner = user
                vm.save()

                # Save the assignment in UserAssignedVM
                UserAssignedVM.objects.create(new_owner=user, vm=vm)

                # Get recipient's email (user's email)
                recipient_email = user.email
                vm_name = vm.name
                user_name = user.username

                # Send email notification
                self.send_assignment_email(recipient_email, user_name, vm_name)

                return Response(
                    {
                        "message": f"Virtual machine '{vm.name}' assigned to user '{user.username}' successfully.",
                        "success": True,
                        "statusCode": 200
                    },
                    status=status.HTTP_200_OK
                )
            except (CustomUser.DoesNotExist, VirtualMachine.DoesNotExist):
                return Response(
                    {
                        "message": "Invalid user or virtual machine ID.",
                        "success": False,
                        "statusCode": 500
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_assignment_email(self, recipient_email, username, vm_name):
        try:
            # SMTP configuration loaded from environment variables
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = os.getenv('SMTP_PORT')
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')

            # Email content
            subject = "VM Assignment Notification"
            body = f"Hello {username},\n\nYou have been assigned the virtual machine '{vm_name}'.\n\nBest regards,\nVM Management Team"

            # Prepare the email
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Establish connection to the SMTP server
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()  # Upgrade the connection to secure
            server.login(smtp_user, smtp_password)

            # Send email
            server.sendmail(smtp_user, recipient_email, msg.as_string())

            # Close the SMTP connection
            server.quit()

            print(f"Email sent successfully to {recipient_email}")

        except Exception as e:
            print(f"Failed to send email. Error: {e}")



class PaymentView(APIView):
    permission_classes = [IsAuthenticated]  # Requires authentication

    def post(self, request):
        # Get the authenticated user from the access token
        user = request.user

        # Attach the user to the data and pass it to the serializer
        data = request.data.copy()
        data['user'] = user.id

        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # Save payment and update the backup status
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UnpaidBackupDetailsView(APIView):

    def get(self, request):
        # Extract user ID from the token
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        
        try:
            decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
            user_id = decoded_token['user_id']  # Adjust based on your token payload structure
            user = User.objects.get(pk=user_id)
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_401_UNAUTHORIZED)

        # Query unpaid backups for this user
        unpaid_backups = Backup.objects.filter(vm__owner=user, status='unpaid')
        
        if not unpaid_backups.exists():
            return Response({"message": "No unpaid backups found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare the response data with only backup details
        backup_details = [
            {
                "vm_name": backup.vm.name,
                "size": backup.size,
                "bill": backup.bill,
                "created_at": backup.created_at,
                "status": backup.status,
            }
            for backup in unpaid_backups
        ]

        return Response({
            "data": backup_details,
            "success": True,
            "statusCode": 200
            }, status=status.HTTP_200_OK)



class CreateBackupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract data from the request
        vm_id = request.data.get('vm')
        size = request.data.get('size')
        bill = request.data.get('bill')

        # Check if the virtual machine exists
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
        except VirtualMachine.DoesNotExist:
            return Response({
                'message': 'Virtual Machine does not exist',
                "success": False,
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

        # Create the Backup instance using the validated data
        backup_data = {
            'vm': vm,
            'size': size,
            'bill': bill,
            'status': 'unpaid'
        }

        backup_serializer = BackupSerializer(data=backup_data)
        if backup_serializer.is_valid():
            backup_serializer.save()
            # Set unbacked_data to zero in the Virtual Machine
            vm.unbacked_data = 0.0
            vm.save()

            return Response({
                "success": True,
                "message": "Backup created successfully",
                "data": backup_serializer.data,
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Invalid data',
                'errors': backup_serializer.errors,
                "success": False,
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)



class CreateSubUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get parent user from the token
        parent_user = request.user

        # Extract data from the request
        sub_username = request.data.get('sub_username')
        assigned_model = request.data.get('assigned_model')

        # Check if sub_username already exists
        if SubUser.objects.filter(sub_username=sub_username).exists():
            return Response({
                'message': 'Sub user already exists',
                "success": False,
                "statusCode": 400
                }, status=status.HTTP_400_BAD_REQUEST)

        # Create the SubUser instance
        sub_user = SubUser.objects.create(
            parent=parent_user,
            sub_username=sub_username,
            assigned_model=assigned_model
        )

        # Serialize the sub_user data and return the response
        serializer = SubUserSerializer(sub_user)
        return Response({
            "success": True,
            "message": "Sub User created successfully",
            "data": serializer.data,
            "statusCode": 200
        }, status=status.HTTP_201_CREATED)


class ListSubUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the parent user from the token
        parent_user = request.user

        # Query all sub-users that belong to this parent user
        sub_users = SubUser.objects.filter(parent=parent_user)

        # Serialize the sub-user data
        serializer = SubUserSerializer(sub_users, many=True)

        # Return the serialized data
        return Response({
            "data":serializer.data,
            "success": True,
            "statusCode": 200
            }, status=status.HTTP_200_OK)



class DeleteVMAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, vm_id):
        vm = get_object_or_404(VirtualMachine, id=vm_id)

        if vm.owner != request.user:
            return Response({"error": "You do not have permission to delete this VM."}, status=status.HTTP_403_FORBIDDEN)
        
        vm.delete()

        return Response({"message": "Virtual machine deleted successfully."}, status=status.HTTP_200_OK)



class VirtualMachineEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vm(self, pk, user):
        try:
            return VirtualMachine.objects.get(pk=pk, owner=user)
        except VirtualMachine.DoesNotExist:
            return None

    def put(self, request, vm_id):
        vm = self.get_vm(vm_id, request.user)
        if not vm:
            return Response({"error": "Virtual Machine not found or you do not have permission to edit."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VirtualMachineSerializer(vm, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Virtual Machine updated successfully", "virtual_machine": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StandardUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        # Get the 'Standard User' role
        standard_user_role = Role.objects.get(name='Standard User')
        
        # Filter users who have this role
        return CustomUser.objects.filter(role=standard_user_role)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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




class AssignedVirtualMachinesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        assigned_vms = UserAssignedVM.objects.filter(new_owner=user)

        vms = [user_assigned.vm for user_assigned in assigned_vms]

        # Serialize the virtual machines
        serializer = VirtualMachineSerializers(vms, many=True)

        return Response({
            "success": True,
            "message": "Assigned virtual machines retrieved successfully",
            "data": serializer.data,
            "statusCode": 200
        }, status=status.HTTP_200_OK)





class MoveVirtualMachineView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, vm_id):
        user = request.user
        
        # Only allow Admin users to move VMs
        if user.role.name != 'Standard User':
            return Response({
                "success": False,
                "message": "Permission denied. You don't have rights to perform this action.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Get the VM to move
        try:
            virtual_machine = VirtualMachine.objects.get(id=vm_id)
        except VirtualMachine.DoesNotExist:
            return Response({
                "success": False,
                "message": "Virtual machine not found.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

        # Deserialize and validate the new owner
        serializer = MoveVirtualMachineSerializer(data=request.data)
        if serializer.is_valid():
            new_owner = serializer.validated_data['new_owner']

            # Move the VM to the new owner
            virtual_machine.owner = new_owner
            virtual_machine.save()

            # Log the movement of the VM
            AuditLog.objects.create(
                user=user,
                action='vm_moved',
                description=f"Virtual machine '{virtual_machine.name}' was moved to user '{new_owner.username}'."
            )

            return Response({
                "success": True,
                "message": "Virtual machine moved successfully.",
                "virtual_machine": {
                    "id": virtual_machine.id,
                    "name": virtual_machine.name,
                    "new_owner": new_owner.username,
                    "moved_by": user.username,
                    "statusCode": 200
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


class ViewBillingInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Check if the user has the 'Standard User' role
        if user.role.name != 'Standard User':
            return Response({
                "success": False,
                "message": "Permission denied. Only Standard Users can view billing information.",
                "statusCode": 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Get the user's payments (assuming Payment model has a relation to the user or subscription)
        payments = Payment.objects.filter(user=user)  # Modify if linked through subscription

        if not payments.exists():
            return Response({
                "success": False,
                "message": "No billing information found.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the billing information
        serializer = BillingSerializer(payments, many=True)
        return Response({
            "success": True,
            "message": "Billing information retrieved successfully.",
            "billing_info": serializer.data,
            "statusCode": 200
        }, status=status.HTTP_200_OK)


class SubscribePlanView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_name = request.data.get('plan')
        plan = get_object_or_404(SubscriptionPlan, name=plan_name)

        # Create a new subscription without checking for existing subscriptions
        subscription = UserSubscription.objects.create(
            user=request.user,
            subscription_plan=plan,
            started_at=timezone.now(),
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )

        # Create payment record
        Payment.objects.create(
            user=request.user,
            subscription_plan=plan,
            amount=plan.cost,
            status='paid',
            transaction_id='mock_transaction_id'  # Mock ID for testing
        )

        return Response({
            "success": True,
            "message": f"Successfully subscribed to {plan_name} plan.",
            "subscription": UserSubscriptionSerializer(subscription).data,
            "statusCode": 201
        }, status=status.HTTP_201_CREATED)


class CreateSubscriptionPlanView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            subscription_plan = serializer.save()
            return Response({
                "success": True,
                "message": "Subscription plan created successfully.",
                "subscription_plan": serializer.data,
                "statusCode": 201
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Invalid data.",
            "errors": serializer.errors,
            "statusCode": 400
        }, status=status.HTTP_400_BAD_REQUEST)


class DeleteSubscriptionPlanView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    def delete(self, request, *args, **kwargs):
        plan = get_object_or_404(SubscriptionPlan, pk=kwargs.get('pk'))
        
        # Optional: Check if there are any active subscriptions associated with this plan
        if UserSubscription.objects.filter(subscription_plan=plan, expires_at__gt=timezone.now()).exists():
            return Response({
                "success": False,
                "message": "Cannot delete subscription plan with active subscriptions.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan.delete()
        return Response({
            "success": True,
            "message": "Subscription plan deleted successfully.",
            "statusCode": 204
        }, status=status.HTTP_204_NO_CONTENT)


class CurrentSubscriptionView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer

    def get(self, request):
        subscription = get_object_or_404(UserSubscription, user=request.user)

        return Response({
            "success": True,
            "message": "Subscription details retrieved successfully.",
            "subscription": UserSubscriptionSerializer(subscription).data,
            "statusCode": 200
        }, status=status.HTTP_200_OK)


# Make Payment (Mock)
class MockPaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        card_number = request.data.get('card_number')
        amount = request.data.get('amount')

        if not card_number or len(card_number) != 16:
            return Response({
                "success": False,
                "message": "Invalid card number.",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Mock payment processing
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            status='paid',
            transaction_id=f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )

        return Response({
            "success": True,
            "message": "Payment successful.",
            "transaction_id": payment.transaction_id,
            "statusCode": 200
        }, status=status.HTTP_200_OK)


# View Payment History
class PaymentHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)

        if not payments.exists():
            return Response({
                "success": False,
                "message": "No payment history found.",
                "statusCode": 404
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "success": True,
            "message": "Payment history retrieved successfully.",
            "payments": PaymentSerializer(payments, many=True).data,
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
