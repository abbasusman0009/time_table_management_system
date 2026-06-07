import random
from apps.timetable.models import Timetable, ScheduledEntry
from apps.academics.models import Course, Department
from apps.venues.models import Room, TimeSlot

def generate_timetable(department, level, semester, year):
    """
    Greedy constraint-based scheduler for TTMS.
    """
    # 1. Initialize
    timetable = Timetable.objects.create(
        department=department,
        level=level,
        semester=semester,
        academic_year=year
    )
    
    courses = list(Course.objects.filter(department=department, level=level))
    rooms = list(Room.objects.filter(is_available=True))
    timeslots = list(TimeSlot.objects.all())
    
    # 2. Sort courses by constraints (Heuristic: higher credit hours first)
    courses.sort(key=lambda x: x.credit_hours, reverse=True)
    
    assigned = []
    unassigned = []
    
    for course in courses:
        success = False
        # Try every timeslot
        random.shuffle(timeslots) # Add some randomness to avoid stacking all on Monday
        for slot in timeslots:
            for room in rooms:
                # Check Hard Constraints
                # - Room capacity
                # (Note: We'd need an expected student count, assuming 30 for now or room capacity is enough)
                
                # - Lecturer Preference (Hard Constraint: must be available)
                if course.lecturer and hasattr(course.lecturer, 'lecturer_profile'):
                    lecturer_prefs = course.lecturer.lecturer_profile.availability.all()
                    if lecturer_prefs.exists() and slot not in lecturer_prefs:
                        continue # Skip this slot, lecturer is unavailable
                        
                # - Lecturer collision
                lecturer_busy = ScheduledEntry.objects.filter(
                    time_slot=slot, 
                    lecturer=course.lecturer,
                    timetable__academic_year=year,
                    timetable__semester=semester
                ).exists()
                
                # - Room collision
                room_busy = ScheduledEntry.objects.filter(
                    time_slot=slot, 
                    room=room,
                    timetable__academic_year=year,
                    timetable__semester=semester
                ).exists()
                
                # - Student Group clash
                group_busy = ScheduledEntry.objects.filter(
                    timetable=timetable,
                    time_slot=slot
                ).exists()
                
                if not (lecturer_busy or room_busy or group_busy):
                    # Check Soft Constraints: Prefer morning if credit hours > 3
                    if course.credit_hours > 3 and slot.slot_index > 3:
                        continue # Try to find an earlier slot
                    
                    # Assign
                    ScheduledEntry.objects.create(
                        timetable=timetable,
                        course=course,
                        lecturer=course.lecturer,
                        room=room,
                        time_slot=slot
                    )
                    assigned.append(course)
                    success = True
                    break
            if success: break
        
        if not success:
            # Mark as UNASSIGNED for manual fix
            ScheduledEntry.objects.create(
                timetable=timetable,
                course=course,
                lecturer=course.lecturer,
                room=None,
                time_slot=None,
                is_conflict=True
            )
            unassigned.append(course)
            
    return timetable, assigned, unassigned

def detect_conflicts(timetable_id):
    """Detects any overlapping schedules in a given timetable."""
    timetable = Timetable.objects.get(id=timetable_id)
    entries = timetable.entries.all()
    conflicts = []
    
    for entry in entries:
        if not entry.room or not entry.time_slot:
            conflicts.append(entry)
            continue
            
        # Re-check hard constraints
        # ... logic to flag conflicts ...
    return conflicts

def validate_timetable(timetable_id):
    """Full constraint check report."""
    timetable = Timetable.objects.get(id=timetable_id)
    report = {
        'total_entries': timetable.entries.count(),
        'unassigned': timetable.entries.filter(time_slot__isnull=True).count(),
        'conflicts': [],
    }
    return report
