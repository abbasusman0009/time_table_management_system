from django.db import models
from django.conf import settings
from apps.academics.models import Department, Course
from apps.venues.models import Room, TimeSlot

class Timetable(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.IntegerField(choices=Course.LEVEL_CHOICES)
    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.department.code} - {self.level}L - {self.semester} ({self.academic_year})"

class ScheduledEntry(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, blank=True)
    is_conflict = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Scheduled Entries"

    def __str__(self):
        return f"{self.course.code} - {self.time_slot if self.time_slot else 'UNASSIGNED'}"

class ConflictReport(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conflict_reports')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.student.username}: {self.subject}"
