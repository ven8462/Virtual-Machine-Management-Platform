# from django.shortcuts import render
# from rest_framework import viewsets, permissions
# from .models import CustomUser
# from .serializers import UserSerializer, UserCreateSerializer

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserCreateSerializer
#         return UserSerializer

#     def get_permissions(self):
#         if self.action == 'create':
#             return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
#         elif self.action in ['update', 'partial_update', 'destroy']:
#             return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
#         return [permissions.IsAuthenticated()]

#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'ADMIN':
#             return CustomUser.objects.all()
#         return CustomUser.objects.filter(id=user.id)