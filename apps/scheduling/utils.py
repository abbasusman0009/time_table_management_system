import csv
from io import TextIOWrapper
from apps.academics.models import Department, Course, LecturerProfile
from apps.venues.models import Room
from apps.accounts.models import CustomUser

def import_data_from_csv(file, type):
    f = TextIOWrapper(file, encoding='utf-8')
    reader = csv.DictReader(f)
    created_count = 0
    errors = []

    for row in reader:
        try:
            if type == 'dept':
                Department.objects.get_or_create(
                    code=row['code'],
                    defaults={'name': row['name'], 'faculty': row.get('faculty', '')}
                )
            elif type == 'course':
                dept = Department.objects.get(code=row['dept_code'])
                lec_user = CustomUser.objects.get(username=row['lecturer_username'])
                Course.objects.get_or_create(
                    code=row['code'],
                    defaults={
                        'title': row['title'],
                        'department': dept,
                        'lecturer': lec_user,
                        'credit_hours': int(row.get('credits', 3)),
                        'level': int(row.get('level', 100))
                    }
                )
            elif type == 'room':
                Room.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'capacity': int(row.get('capacity', 50)),
                        'room_type': row.get('type', 'lecture_hall')
                    }
                )
            created_count += 1
        except Exception as e:
            errors.append(f"Row {row}: {str(e)}")

    return created_count, errors
