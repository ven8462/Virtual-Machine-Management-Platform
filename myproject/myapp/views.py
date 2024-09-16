from rest_framework import viewsets
from .models import VirtualMachine, Backup, Snapshot, Payment, SubscriptionPlan, UserSubscription, AuditLog
from .serializers import VirtualMachineSerializer, BackupSerializer, SnapshotSerializer, PaymentSerializer, SubscriptionPlanSerializer, UserSubscriptionSerializer, AuditLogSerializer

class VirtualMachineViewSet(viewsets.ModelViewSet):
    queryset = VirtualMachine.objects.all()
    serializer_class = VirtualMachineSerializer

class BackupViewSet(viewsets.ModelViewSet):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer

class SnapshotViewSet(viewsets.ModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
