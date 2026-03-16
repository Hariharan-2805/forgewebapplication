from django.contrib import admin
from .models import Queue, Token, Notification, QueueAnalytics

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active', 'created_at', 'avg_wait_time_per_person')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('queue', 'user', 'number', 'status', 'created_at')
    list_filter = ('status', 'queue')
    search_fields = ('user__username', 'queue__name')

admin.site.register(Notification)
admin.site.register(QueueAnalytics)
