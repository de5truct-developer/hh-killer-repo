from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancies/<int:pk>/apply/', views.apply_vacancy, name='apply_vacancy'),
    path('vacancies/<int:pk>/save/', views.toggle_save_vacancy, name='toggle_save_vacancy'),
    path('vacancies/<int:pk>/edit/', views.edit_vacancy, name='edit_vacancy'),
    path('vacancies/<int:pk>/delete/', views.delete_vacancy, name='delete_vacancy'),
    path('vacancies/<int:pk>/applications/', views.vacancy_applications, name='vacancy_applications'),
    path('vacancies/create/', views.create_vacancy, name='create_vacancy'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:pk>/chat/', views.application_chat, name='application_chat'),
    path('saved/', views.saved_vacancies, name='saved_vacancies'),
    path('recommendations/', views.recommendations, name='recommendations'),
]
