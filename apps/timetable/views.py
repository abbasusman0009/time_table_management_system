from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponse
from .models import Timetable, ScheduledEntry
from apps.venues.models import Room, TimeSlot
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from io import BytesIO
import csv
from apps.academics.models import Department, Course
from apps.accounts.models import CustomUser

class StudentTimetableView(LoginRequiredMixin, ListView):
    model = ScheduledEntry
    template_name = 'student/timetable.html'
    context_object_name = 'entries'

    def get_queryset(self):
        latest_timetable = Timetable.objects.filter(
            department=self.request.user.department,
            level=self.request.user.level,
            is_published=True
        ).order_by('-created_at').first()

        if latest_timetable:
            return latest_timetable.entries.select_related('course', 'room', 'time_slot')
        return ScheduledEntry.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['days'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        context['timeslots'] = TimeSlot.objects.order_by('slot_index')
        context['department'] = self.request.user.department
        context['level'] = self.request.user.level
        return context

class LecturerScheduleView(LoginRequiredMixin, ListView):
    model = ScheduledEntry
    template_name = 'lecturer/schedule.html'
    context_object_name = 'entries'

    def get_queryset(self):
        return ScheduledEntry.objects.filter(
            lecturer=self.request.user
        ).select_related('course', 'room', 'time_slot')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['days'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        context['timeslots'] = TimeSlot.objects.order_by('slot_index')
        return context

def export_lecturer_pdf(request):
    entries = ScheduledEntry.objects.filter(lecturer=request.user).select_related('course', 'room', 'time_slot')
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph(f"<b>Teaching Schedule: {request.user.get_full_name()}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    all_slots = list(TimeSlot.objects.order_by('slot_index'))
    
    data = [['Day / Time'] + [f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}" for s in all_slots]]
    
    for day in days:
        row = [day]
        for slot in all_slots:
            cell_entries = entries.filter(time_slot=slot, time_slot__day=day)
            if cell_entries.exists():
                texts = [f"{e.course.code}\n{e.room.name if e.room else 'No Room'}" for e in cell_entries]
                row.append("\n\n".join(texts))
            else:
                row.append("")
        data.append(row)
        
    t = Table(data, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0,0), (-1,-1), True)
    ])
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="teaching_schedule_{request.user.username}.pdf"'
    return response

def export_lecturer_excel(request):
    entries = ScheduledEntry.objects.filter(lecturer=request.user).select_related('course', 'room', 'time_slot')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="teaching_schedule_{request.user.username}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Course Code', 'Course Title', 'Room', 'Department', 'Level'])
    
    # Sort entries by day and time
    day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
    sorted_entries = sorted(list(entries), key=lambda x: (day_order.get(x.time_slot.day, 99) if x.time_slot else 99, x.time_slot.start_time if x.time_slot else ''))
    
    for entry in sorted_entries:
        if entry.time_slot:
            writer.writerow([
                entry.time_slot.day,
                entry.time_slot.start_time.strftime('%H:%M'),
                entry.time_slot.end_time.strftime('%H:%M'),
                entry.course.code,
                entry.course.title,
                entry.room.name if entry.room else 'Unassigned',
                entry.timetable.department.code,
                f"{entry.timetable.level}L"
            ])
    
    return response

class AdminTimetableEditView(LoginRequiredMixin, DetailView):
    model = Timetable
    template_name = 'admin/timetable_edit.html'
    context_object_name = 'timetable'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entries'] = self.object.entries.all().order_by('time_slot__slot_index')
        context['rooms'] = Room.objects.all()
        context['timeslots'] = TimeSlot.objects.all()
        context['days'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        context['has_conflicts'] = context['entries'].filter(is_conflict=True).exists()
        return context

    def post(self, request, pk):
        timetable = get_object_or_404(Timetable, id=pk)
        action = request.POST.get('action')
        
        if action == 'publish':
            if not timetable.is_published:
                # Unpublish older timetables for the same dept/level/semester
                Timetable.objects.filter(
                    department=timetable.department,
                    level=timetable.level,
                    semester=timetable.semester,
                    academic_year=timetable.academic_year,
                    is_published=True
                ).update(is_published=False)

            timetable.is_published = not timetable.is_published
            timetable.save()
            status = "published" if timetable.is_published else "unpublished"
            
            if timetable.is_published:
                from apps.accounts.models import CustomUser, Notification
                students = CustomUser.objects.filter(role='student', department=timetable.department, level=timetable.level)
                explorer_link = f"/timetable/explorer/?department={timetable.department.id}&level={timetable.level}"
                notifs = [Notification(user=s, message=f"The timetable for {timetable.department.code} {timetable.level}L is now published.", link=explorer_link) for s in students]
                Notification.objects.bulk_create(notifs)

            messages.success(request, f"Timetable {status} successfully.")
            return redirect('timetable:admin_timetable_edit', pk=pk)

        # Handle manual adjustments
        entry_id = request.POST.get('entry_id')
        slot_id = request.POST.get('slot_id')
        room_id = request.POST.get('room_id')
        
        entry = get_object_or_404(ScheduledEntry, id=entry_id)
        if slot_id: entry.time_slot_id = slot_id
        if room_id: entry.room_id = room_id
        entry.is_conflict = False # Reset flag after manual fix
        entry.save()
        
        return redirect('timetable:admin_timetable_edit', pk=pk)

def export_timetable_pdf(request, pk):
    timetable = get_object_or_404(Timetable, id=pk)
    entries = timetable.entries.all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph(f"<b>Timetable: {timetable.department.code} {timetable.level}L</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Build grid data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    # Extract unique timeslots sorted
    all_slots = list(set(e.time_slot for e in entries if e.time_slot))
    all_slots.sort(key=lambda x: x.slot_index)
    
    # Header row
    data = [['Day / Time'] + [f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}" for s in all_slots]]
    
    for day in days:
        row = [day]
        for slot in all_slots:
            cell_entries = entries.filter(time_slot=slot, time_slot__day=day)
            if cell_entries.exists():
                texts = [f"{e.course.code}\n{e.room.name if e.room else 'No Room'}" for e in cell_entries]
                row.append("\n\n".join(texts))
            else:
                row.append("")
        data.append(row)
        
    t = Table(data, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0,0), (-1,-1), True)
    ])
    
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timetable_{timetable.department.code}_{timetable.level}.pdf"'
    return response

def export_timetable_excel(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    entries = timetable.entries.select_related('course', 'room', 'time_slot', 'lecturer')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="timetable_{timetable.department.code}_{timetable.level}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Course Code', 'Course Title', 'Room', 'Lecturer'])
    
    # Sort entries by day and time
    day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5}
    sorted_entries = sorted(list(entries), key=lambda x: (day_order.get(x.time_slot.day, 99) if x.time_slot else 99, x.time_slot.start_time if x.time_slot else ''))
    
    for entry in sorted_entries:
        if entry.time_slot:
            writer.writerow([
                entry.time_slot.day,
                entry.time_slot.start_time.strftime('%H:%M'),
                entry.time_slot.end_time.strftime('%H:%M'),
                entry.course.code,
                entry.course.title,
                entry.room.name if entry.room else 'Unassigned',
                entry.lecturer.get_full_name() if entry.lecturer else 'Unassigned'
            ])
    
    return response

class AdminTimetableHistoryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Timetable
    template_name = 'admin/timetable_history.html'
    context_object_name = 'timetables'
    ordering = ['-created_at']

    def test_func(self):
        return self.request.user.role == 'admin'

class TimetableExplorerView(LoginRequiredMixin, TemplateView):
    template_name = 'timetable/explorer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter options
        context['departments'] = Department.objects.all()
        context['levels'] = [100, 200, 300, 400, 500]
        context['courses'] = Course.objects.all()
        context['lecturers'] = CustomUser.objects.filter(role='lecturer')
        context['days'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        context['timeslots'] = TimeSlot.objects.order_by('slot_index')

        # Current filters
        dept_id = self.request.GET.get('department')
        level = self.request.GET.get('level')
        course_id = self.request.GET.get('course')
        lecturer_id = self.request.GET.get('lecturer')

        # Maintain selected filters in context for the UI
        context['selected_dept'] = int(dept_id) if dept_id and dept_id.isdigit() else ''
        context['selected_level'] = int(level) if level and level.isdigit() else ''
        context['selected_course'] = int(course_id) if course_id and course_id.isdigit() else ''
        context['selected_lecturer'] = int(lecturer_id) if lecturer_id and lecturer_id.isdigit() else ''

        # Build Queryset
        entries = ScheduledEntry.objects.filter(timetable__is_published=True).select_related('course', 'room', 'time_slot', 'timetable__department', 'lecturer')
        
        has_filters = False
        if dept_id:
            entries = entries.filter(timetable__department_id=dept_id)
            has_filters = True
        if level:
            entries = entries.filter(timetable__level=level)
            has_filters = True
        if course_id:
            entries = entries.filter(course_id=course_id)
            has_filters = True
        if lecturer_id:
            entries = entries.filter(lecturer_id=lecturer_id)
            has_filters = True

        # Only return entries if the user actually clicked Search (has_filters)
        if has_filters:
            context['entries'] = entries
        else:
            context['entries'] = ScheduledEntry.objects.none()
            
        context['has_searched'] = has_filters
        return context

class SubmitFeedbackView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        from .models import ConflictReport
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if subject and message:
            ConflictReport.objects.create(
                student=request.user,
                subject=subject,
                message=message
            )
            messages.success(request, "Your report has been submitted to the admin.")
        else:
            messages.error(request, "Subject and message are required.")
            
        return redirect('timetable:student_dashboard')

class AdminFeedbackListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Timetable # Dummy, using specific query
    template_name = 'admin/feedback_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        from .models import ConflictReport
        return ConflictReport.objects.select_related('student').order_by('-created_at')

    def test_func(self):
        return self.request.user.role == 'admin'

