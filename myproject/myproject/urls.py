from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import VirtualMachineViewSet, ViewBillingInfoView, MoveVirtualMachineView, CreateBackupView, DeleteVirtualMachineView, UpdateVirtualMachineView, UserVirtualMachinesView, CreateVirtualMachineView, BackupViewSet, SnapshotViewSet, PaymentViewSet, SubscriptionPlanViewSet, UserSubscriptionViewSet, AuditLogViewSet, SignUpView, LoginView
from myapp.views import SubscribePlanView, CurrentSubscriptionView, DeleteSubscriptionPlanView, MockPaymentView, PaymentHistoryView, CreateSubscriptionPlanView

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
    path('api/vms/update/<int:vm_id>/', UpdateVirtualMachineView.as_view(), name='update-vm'),
    path('api/vms/delete/<int:vm_id>/', DeleteVirtualMachineView.as_view(), name='delete-vm'),
    path('api/create-backup/', CreateBackupView.as_view(), name='create-backup'),
    path('api/virtual-machines/<int:vm_id>/move/', MoveVirtualMachineView.as_view(), name='move-virtual-machine'),
    path('api/billing-info/', ViewBillingInfoView.as_view(), name='view-billing-info'),
    path('api/subscribe/', SubscribePlanView.as_view(), name='subscribe_plan'),
    path('api/subscription/', CurrentSubscriptionView.as_view(), name='current_subscription'),
    path('api/payment/', MockPaymentView.as_view(), name='make_payment'),
    path('api/payment-history/', PaymentHistoryView.as_view(), name='payment_history'),
    path('api/create-subscription-plan/', CreateSubscriptionPlanView.as_view(), name='create_subscription_plan'),
    path('api/delete-subscription-plan/<int:pk>/', DeleteSubscriptionPlanView.as_view(), name='delete_subscription_plan'),
]
