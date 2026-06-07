from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Department, Course, LecturerProfile
from .forms import DepartmentForm, CourseForm, LecturerForm
from apps.accounts.models import CustomUser

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

# Department Views
class DepartmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Department
    template_name = 'admin/academics/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'admin/academics/department_form.html'
    success_url = reverse_lazy('academics:department_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Department created successfully.")
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'admin/academics/department_form.html'
    success_url = reverse_lazy('academics:department_list')

    def form_valid(self, form):
        messages.success(self.request, "Department updated successfully.")
        return super().form_valid(form)

# Course Views
class CourseListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Course
    template_name = 'admin/academics/course_list.html'
    context_object_name = 'courses'

class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'admin/academics/course_form.html'
    success_url = reverse_lazy('academics:course_list')

    def form_valid(self, form):
        messages.success(self.request, "Course created successfully.")
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'admin/academics/course_form.html'
    success_url = reverse_lazy('academics:course_list')

# Lecturer Views
class LecturerListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = LecturerProfile
    template_name = 'admin/academics/lecturer_list.html'
    context_object_name = 'lecturers'

class LecturerCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = LecturerForm
    template_name = 'admin/academics/lecturer_form.html'
    success_url = reverse_lazy('academics:lecturer_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = 'lecturer'
        user.is_approved = True
        user.save()
        # Create profile
        LecturerProfile.objects.create(
            user=user,
            staff_id=form.cleaned_data.get('staff_id'),
            specialization=form.cleaned_data.get('specialization')
        )
        messages.success(self.request, "Lecturer created successfully.")
        return redirect(self.success_url)

class LecturerDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = LecturerProfile
    template_name = 'admin/academics/lecturer_detail.html'
    context_object_name = 'lecturer'

class LecturerPreferencesView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LecturerProfile
    fields = ['availability']
    template_name = 'lecturer/preferences.html'
    success_url = reverse_lazy('timetable:lecturer_dashboard')

    def test_func(self):
        return self.request.user.role == 'lecturer'

    def get_object(self):
        return self.request.user.lecturer_profile

    def form_valid(self, form):
        messages.success(self.request, "Your availability preferences have been updated.")
        return super().form_valid(form)
