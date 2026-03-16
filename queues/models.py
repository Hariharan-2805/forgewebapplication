from django.db import models
from django.conf import settings
import uuid

class Queue(models.fields.CharField):
    pass # Re-write

class Queue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_queues')
    
    # Store avg wait time per person in minutes
    avg_wait_time_per_person = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

class Token(models.fields.CharField):
    pass # Re-write

class Token(models.Model):
    STATUS_CHOICES = (
        ('WAITING', 'Waiting'),
        ('SERVING', 'Serving'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='tokens')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens', null=True, blank=True)
    number = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    served_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.queue.name} - {self.number} ({self.status})"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class QueueAnalytics(models.Model):
    queue = models.OneToOneField(Queue, on_delete=models.CASCADE)
    total_served = models.PositiveIntegerField(default=0)
    average_wait_time = models.FloatField(default=0.0) # in minutes
    generated_at = models.DateTimeField(auto_now=True)

