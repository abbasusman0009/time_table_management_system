from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    level = models.IntegerField(choices=[(100, '100'), (200, '200'), (300, '300'), (400, '400'), (500, '500')], default=100)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    registered_courses = models.ManyToManyField('academics.Course', blank=True, related_name='registered_students')

    def is_admin(self):
        return self.role == 'admin'

    def is_lecturer(self):
        return self.role == 'lecturer'

    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Optional URL to redirect when clicked")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.user.username}: {self.message}"
