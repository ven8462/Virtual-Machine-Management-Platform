from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    pass

class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class VirtualMachine(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
    ]
    
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Backup(models.Model):
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='backups')
    size = models.FloatField()  
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vm.name} Backup - {self.created_at}"

class Snapshot(models.Model):
    vm = models.ForeignKey(VirtualMachine, on_delete=models.CASCADE, related_name='snapshots')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vm.name} Snapshot - {self.created_at}"



class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment - {self.transaction_id} - {self.status}"


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    max_vms = models.IntegerField()
    max_backups = models.IntegerField()

    def __str__(self):
        return self.name

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
