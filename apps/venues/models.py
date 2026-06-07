from django.db import models

class Room(models.Model):
    ROOM_TYPES = (
        ('lecture_hall', 'Lecture Hall'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar Room'),
    )
    
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()} - Cap: {self.capacity})"

class TimeSlot(models.Model):
    DAYS_OF_WEEK = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    )
    
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_index = models.PositiveIntegerField(help_text="Order of the slot in the day (e.g., 1 for morning)")

    class Meta:
        ordering = ['day', 'slot_index']
        unique_together = ('day', 'slot_index')

    def __str__(self):
        return f"{self.day}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
