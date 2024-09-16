from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import VirtualMachineViewSet, BackupViewSet, SnapshotViewSet, PaymentViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet, AuditLogViewSet


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
]
