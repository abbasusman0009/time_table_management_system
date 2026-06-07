from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __cl__(self):
        return f"{self.name} ({self.code})"

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = (
        (100, '100 Level'),
        (200, '200 Level'),
        (300, '300 Level'),
        (400, '400 Level'),
        (500, '500 Level'),
    )
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    credit_hours = models.PositiveIntegerField()
    level = models.IntegerField(choices=LEVEL_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'lecturer'})
    duration_hours = models.PositiveIntegerField(default=1, help_text="Duration of a single class session")

    def __str__(self):
        return f"{self.code}: {self.title}"

class LecturerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=255)
    # availability back-references TimeSlot in Venues app
    availability = models.ManyToManyField('venues.TimeSlot', blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
