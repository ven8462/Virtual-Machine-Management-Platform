from django.test import TestCase
from django.utils import timezone
from .models import CustomUser, Role, SubUser, VirtualMachine, UserAssignedVM, Backup, Snapshot, SubscriptionPlan, Payment, UserSubscription, AuditLog



class TestModels(TestCase):

    def setUp(self):
        # Create roles
        self.role = Role.objects.create(name='Admin', description='Admin role')

        # Create users
        self.user = CustomUser.objects.create_user(username='parent_user', password='password123', role=self.role)
        self.sub_user = CustomUser.objects.create_user(username='sub_user', password='password123')

        # Create a virtual machine
        self.vm = VirtualMachine.objects.create(owner=self.user, name='Test VM', status='running')

        # Create a subscription plan
        self.plan = SubscriptionPlan.objects.create(name='gold', max_vms=5, max_backups=10, cost=100.00)

    # Test Role model
    def test_role_creation(self):
        role = Role.objects.create(name='Standard User', description='Default role')
        self.assertEqual(role.name, 'Standard User')
        self.assertEqual(role.description, 'Default role')

    # Test CustomUser model
    def test_custom_user_creation(self):
        user = CustomUser.objects.create_user(username='new_user', password='password123', role=self.role)
        self.assertEqual(user.username, 'new_user')
        self.assertEqual(user.role, self.role)

    # Test SubUser model
    def test_sub_user_creation(self):
        sub_user = SubUser.objects.create(parent=self.user, sub_username='sub_user_1', assigned_model=1.0)
        self.assertEqual(sub_user.parent, self.user)
        self.assertEqual(sub_user.sub_username, 'sub_user_1')

    # Test VirtualMachine model
    def test_virtual_machine_creation(self):
        vm = VirtualMachine.objects.create(owner=self.user, name='VM 1', status='running')
        self.assertEqual(vm.owner, self.user)
        self.assertEqual(vm.name, 'VM 1')
        self.assertEqual(vm.status, 'running')

    # Test UserAssignedVM model
    def test_user_assigned_vm(self):
        user_assigned_vm = UserAssignedVM.objects.create(new_owner=self.sub_user, vm=self.vm)
        self.assertEqual(user_assigned_vm.new_owner, self.sub_user)
        self.assertEqual(user_assigned_vm.vm, self.vm)

    def test_user_assigned_vm_unique_constraint(self):
        UserAssignedVM.objects.create(new_owner=self.sub_user, vm=self.vm)
        with self.assertRaises(Exception):
            UserAssignedVM.objects.create(new_owner=self.sub_user, vm=self.vm)  # This should fail due to unique_together

    # Test Backup model
    def test_backup_creation(self):
        backup = Backup.objects.create(vm=self.vm, size=10.0)
        self.assertEqual(backup.vm, self.vm)
        self.assertEqual(backup.size, 10.0)
        self.assertEqual(backup.status, 'unpaid')

    # Test Snapshot model
    def test_snapshot_creation(self):
        snapshot = Snapshot.objects.create(vm=self.vm)
        self.assertEqual(snapshot.vm, self.vm)

    # Test SubscriptionPlan model
    def test_subscription_plan_creation(self):
        plan = SubscriptionPlan.objects.create(name='platinum', max_vms=10, max_backups=20, cost=150.00)
        self.assertEqual(plan.name, 'platinum')
        self.assertEqual(plan.max_vms, 10)
        self.assertEqual(plan.cost, 150.00)

    # Test Payment model
    def test_payment_creation(self):
        payment = Payment.objects.create(user=self.user, card_number='1234567890123456', amount=50.00)
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, 50.00)

    # Test UserSubscription model
    def test_user_subscription_creation(self):
        subscription = UserSubscription.objects.create(user=self.user, subscription_plan=self.plan, expires_at=timezone.now() + timezone.timedelta(days=30))
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subscription_plan, self.plan)

    # Test AuditLog model
    def test_audit_log_creation(self):
        audit_log = AuditLog.objects.create(user=self.user, action='vm_created', description='VM was created.')
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'vm_created')
        self.assertEqual(audit_log.description, 'VM was created.')
