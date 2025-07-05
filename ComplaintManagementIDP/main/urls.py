from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),

    # Citizen URLs
    path('citizen/register/', views.citizen_register, name='citizen_register'),
    path('citizen/login/', views.citizen_login, name='citizen_login'),
    path('citizen/dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('citizen/complaint/register/', views.register_complaint, name='register_complaint'),
    path('citizen/complaint/<int:complaint_id>/', views.view_complaint, name='view_complaint'),
    path('citizen/complaint/<int:complaint_id>/feedback/', views.submit_feedback, name='submit_feedback'),

    # Department URLs
    path('department/register/', views.department_register, name='department_register'),
    path('department/login/', views.department_login, name='department_login'),
    path('department/dashboard/', views.department_dashboard, name='department_dashboard'),
    path('department/complaint/<int:complaint_id>/update/', views.update_complaint_status,
         name='update_complaint_status'),

    # Logout
    path('logout/', views.logout_view, name='logout'),
]