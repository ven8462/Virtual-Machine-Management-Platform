from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import VirtualMachineViewSet, UserVirtualMachinesView, CreateVirtualMachineView, BackupViewSet, SnapshotViewSet, PaymentViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet, AuditLogViewSet, SignUpView, LoginView


router = DefaultRouter()
router.register(r'vms', VirtualMachineViewSet)
router.register(r'backups', BackupViewSet)
router.register(r'snapshots', SnapshotViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'user-subscriptions', UserSubscriptionViewSet)
router.register(r'audit-logs', AuditLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'), 
    path('api/create-vms/', CreateVirtualMachineView.as_view(), name='create-vm'),
    path('api/my-vms/', UserVirtualMachinesView.as_view(), name='user-vms'),
]
