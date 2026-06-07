from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .engine import generate_timetable
from apps.academics.models import Department, Course, LecturerProfile
from apps.venues.models import Room
from apps.timetable.models import Timetable, ScheduledEntry

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_courses'] = Course.objects.count()
        context['total_rooms'] = Room.objects.count()
        context['total_lecturers'] = CustomUser.objects.filter(role='lecturer').count()
        context['total_entries'] = ScheduledEntry.objects.count()
        context['conflicts_count'] = ScheduledEntry.objects.filter(is_conflict=True).count()
        context['recent_timetables'] = Timetable.objects.all().order_by('-created_at')[:5]
        context['pending_users'] = CustomUser.objects.filter(role='student', is_approved=False)
        
        # Room Utilization Analytics
        from apps.venues.models import TimeSlot
        total_timeslots = TimeSlot.objects.count()
        room_labels = []
        room_data = []
        if total_timeslots > 0:
            for room in Room.objects.filter(is_available=True):
                used_slots = ScheduledEntry.objects.filter(room=room).count()
                utilization = round((used_slots / total_timeslots) * 100, 1)
                room_labels.append(room.name)
                room_data.append(utilization)
        
        context['room_labels'] = room_labels
        context['room_data'] = room_data
        
        return context

from .utils import import_data_from_csv

class ImportDataView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'admin/import_data.html'

    def test_func(self):
        return self.request.user.role == 'admin'

    def post(self, request, *args, **kwargs):
        data_type = request.POST.get('type')
        csv_file = request.FILES.get('file')
        
        if not csv_file:
            messages.error(request, "Please upload a CSV file.")
            return self.get(request)

        count, errors = import_data_from_csv(csv_file, data_type)
        
        if count > 0:
            messages.success(request, f"Successfully imported {count} items.")
        if errors:
            for err in errors[:5]: # Show first 5 errors
                messages.warning(request, err)
        
        return redirect('scheduling:admin_dashboard')

from apps.accounts.models import CustomUser # Import inside to avoid circularity if needed

class GenerateTimetableView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        departments = Department.objects.filter(is_active=True)
        return render(request, 'admin/generate_form.html', {'departments': departments})

    def post(self, request):
        dept_id = request.POST.get('department')
        level = request.POST.get('level')
        semester = request.POST.get('semester')
        year = request.POST.get('academic_year')
        
        department = get_object_or_404(Department, id=dept_id)
        
        try:
            timetable, assigned, unassigned = generate_timetable(department, level, semester, year)
            messages.success(request, f"Timetable generated! {len(assigned)} classes scheduled, {len(unassigned)} unassigned.")
            return redirect('timetable:admin_timetable_edit', pk=timetable.id)
        except Exception as e:
            messages.error(request, f"Error generating timetable: {str(e)}")
            return redirect('scheduling:generate')

class ConflictResolutionView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ScheduledEntry
    template_name = 'admin/conflicts.html'
    context_object_name = 'conflicted_entries'

    def get_queryset(self):
        return ScheduledEntry.objects.filter(is_conflict=True)
