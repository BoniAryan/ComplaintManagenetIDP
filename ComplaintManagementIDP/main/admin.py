from django.contrib import admin
from .models import Citizen, Department, Complaint, ComplaintLog, Feedback

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ['user', 'contact_number', 'gender', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'user__email', 'contact_number']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'contact_number', 'email']
    search_fields = ['name', 'contact_person', 'email']

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'citizen', 'category', 'department', 'priority', 'date_submitted']
    list_filter = ['priority', 'category', 'department', 'date_submitted']
    search_fields = ['citizen__user__username', 'description']
    readonly_fields = ['date_submitted']

@admin.register(ComplaintLog)
class ComplaintLogAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'rating', 'date_provided']
    list_filter = ['rating', 'date_provided']