from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('join/', views.join_queue, name='join_queue'),
    path('create/', views.create_queue, name='create_queue'),
    path('manage/<int:queue_id>/', views.manage_queue, name='manage_queue'),
    path('manage/<int:queue_id>/toggle/', views.toggle_queue, name='toggle_queue'),
    path('status/<uuid:token_id>/', views.queue_status, name='queue_status'),
    path('verify/<uuid:token_id>/', views.verify_token, name='verify_token'),
]
