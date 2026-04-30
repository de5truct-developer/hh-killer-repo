from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/seeker/', views.register_seeker, name='register_seeker'),
    path('register/employer/', views.register_employer, name='register_employer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/seeker/', views.seeker_profile, name='seeker_profile'),
    path('profile/employer/', views.employer_profile, name='employer_profile'),
    path('profile/seeker/<int:pk>/', views.public_seeker_profile, name='public_seeker_profile'),
    path('profile/employer/<int:pk>/', views.public_employer_profile, name='public_employer_profile'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:pk>/read/', views.read_notification, name='read_notification'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
]
