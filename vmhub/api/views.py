from rest_framework import viewsets, permissions
from users.models import CustomUser
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsAdminUser, IsSelfOrAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Only admins can create users
            return [permissions.IsAuthenticated(), IsAdminUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only admins can update or delete other users, users can update their own profile
            return [permissions.IsAuthenticated(), IsSelfOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Admins can see all users. Standard users only see their own data.
        """
        user = self.request.user
        if user.role == 'ADMIN':
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)