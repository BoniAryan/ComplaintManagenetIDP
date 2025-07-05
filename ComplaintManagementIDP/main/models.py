from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator
from django.utils import timezone
import os
from django.core.exceptions import ValidationError

def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if image.size > max_size:
        raise ValidationError(f'Image size cannot exceed 5MB. Current size: {image.size / (1024*1024):.2f}MB')

def complaint_image_upload_path(instance, filename):
    return f'complaints/{instance.id}/{filename}'

class Citizen(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')]
    )
    address = models.TextField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.contact_number}"


class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Add this line
    name = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=50)
    contact_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')]
    )
    email = models.EmailField(unique=True)
    address = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=50)
    description = models.TextField(
        validators=[
            MinLengthValidator(10, 'Description must be at least 10 characters long.'),
            MaxLengthValidator(1000, 'Description cannot exceed 1000 characters.')
        ]
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='complaints')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    date_submitted = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(
        upload_to='media/complaints/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Upload complaint image (max 5MB)'
    )

    class Meta:
        ordering = ['-date_submitted']

    def __str__(self):
        return f"Complaint #{self.id} - {self.category}"

    def get_latest_status(self):
        latest_log = self.logs.order_by('-timestamp').first()
        return latest_log.status if latest_log else 'Pending'

    def get_latest_remarks(self):
        latest_log = self.logs.order_by('-timestamp').first()
        return latest_log.remarks if latest_log else 'No remarks yet'


class ComplaintLog(models.Model):
    STATUS_CHOICES = [
        ('In-progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Not resolved', 'Not Resolved'),
    ]

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Log for Complaint #{self.complaint.id} - {self.status}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField()
    date_provided = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Complaint #{self.complaint.id} - {self.rating}/5"
