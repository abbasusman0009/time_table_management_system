from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser
from apps.academics.models import Department, Course, LecturerProfile
from apps.venues.models import Room, TimeSlot
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds initial data for Northeastern University TTMS'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")
        
        # 1. Create Admin
        admin, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@neu-gombe.edu.ng', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write("- Admin user created (admin/admin123)")

        # 2. Departments
        cs_dept, _ = Department.objects.get_or_create(name="Computer Science", code="CSC", faculty="Science")
        math_dept, _ = Department.objects.get_or_create(name="Mathematics", code="MTH", faculty="Science")

        # 3. Rooms
        Room.objects.get_or_create(name="Lecture Theater 1", capacity=200, room_type="lecture_hall")
        Room.objects.get_or_create(name="Main Lab", capacity=50, room_type="lab")
        Room.objects.get_or_create(name="Seminar Room B", capacity=30, room_type="seminar")

        # 4. Time Slots (8 AM to 4 PM, 1 hour each)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in days:
            for i in range(8, 16):
                start = datetime.time(i, 0)
                end = datetime.time(i + 1, 0)
                TimeSlot.objects.get_or_create(
                    day=day, 
                    start_time=start, 
                    end_time=end, 
                    slot_index=i-7
                )

        # 5. Lecturers
        l1, c = CustomUser.objects.get_or_create(username='dr.bello', defaults={'first_name': 'Dr.', 'last_name': 'Bello', 'role': 'lecturer'})
        if c: 
            l1.set_password('lecturer123')
            l1.save()
            LecturerProfile.objects.create(user=l1, staff_id="NEU/LEC/001", specialization="Artificial Intelligence")

        l2, c = CustomUser.objects.get_or_create(username='prof.musy', defaults={'first_name': 'Prof.', 'last_name': 'Musa', 'role': 'lecturer'})
        if c:
            l2.set_password('lecturer123')
            l2.save()
            LecturerProfile.objects.create(user=l2, staff_id="NEU/LEC/002", specialization="Pure Mathematics")

        # 6. Courses
        Course.objects.get_or_create(
            code="CSC101", 
            defaults={'title': "Introduction to Computer Science", 'credit_hours': 3, 'level': 100, 'department': cs_dept, 'lecturer': l1}
        )
        Course.objects.get_or_create(
            code="MTH101", 
            defaults={'title': "General Mathematics I", 'credit_hours': 4, 'level': 100, 'department': math_dept, 'lecturer': l2}
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded data!"))
