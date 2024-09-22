from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    @staticmethod
    def get_default_role():
        # You can use get_or_create to avoid duplicates
        role, created = Role.objects.get_or_create(name='Standard User', defaults={'description': 'Default role for new users'})
        return role
    
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_user_permissions',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)


class SubUser(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sub_users')
    sub_username = models.CharField(max_length=150, unique=True)
    assigned_model= models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SubUser: {self.sub_username} (Parent: {self.parent.username})"



    
class VirtualMachine(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
    ]
    
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cpu = models.CharField(max_length=50, default='2 vCPUs')  
    ram = models.CharField(max_length=50, default='4 GB') 
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=20.00) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    unbacked_data = models.FloatField(default=1.0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserAssignedVM(models.Model):
    new_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('new_owner', 'vm')
    def __str__(self):
        return f"{self.new_owner.username} assigned to {self.vm.name}"


class Backup(models.Model):
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='backups')
    size = models.FloatField()  
    bill = models.FloatField(default=0.0)  
    status = models.CharField(max_length=20, default='unpaid')  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vm.name} Backup - {self.created_at}"

class Snapshot(models.Model):
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='snapshots')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vm.name} Snapshot - {self.created_at}"



class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    ]
    
    name = models.CharField(max_length=20, unique=True, choices=PLAN_CHOICES)
    max_vms = models.IntegerField()
    max_backups = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return self.name

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment - {self.transaction_id} - {self.status}"

class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.subscription_plan.name}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('vm_move', 'VM Moved'),
        ('vm_created', 'VM Created'),
        ('vm_deleted', 'VM Deleted'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
