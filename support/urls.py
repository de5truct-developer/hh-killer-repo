from django.urls import path
from . import views

urlpatterns = [
    path('', views.support_home, name='support_home'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/close/', views.close_ticket, name='close_ticket'),
    path('admin-panel/', views.admin_support, name='admin_support'),
]
