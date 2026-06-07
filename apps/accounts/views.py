from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import StudentRegistrationForm, UserLoginForm
from .models import CustomUser

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        user = form.get_user()
        if user.role == 'student' and not user.is_approved:
            messages.error(self.request, "Your account is pending admin approval.")
            return redirect('accounts:login')
        login(self.request, user)
        return redirect('accounts:dashboard_redirect')

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.role == 'admin':
        return redirect('scheduling:admin_dashboard')
    elif request.user.role == 'lecturer':
        return redirect('timetable:lecturer_dashboard')
    else:
        return redirect('timetable:student_dashboard')

class StudentRegistrationView(CreateView):
    model = CustomUser
    form_class = StudentRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = 'student'
        user.is_approved = False  # Pending approval
        user.save()
        messages.success(self.request, "Registration successful! Please wait for admin approval.")
        return super().form_valid(form)

class ApproveStudentView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'admin'

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_approved = True
        user.save()
        messages.success(request, f"Student {user.username} has been approved.")
        return redirect('scheduling:admin_dashboard')

class AdminStudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CustomUser
    form_class = StudentRegistrationForm
    template_name = 'admin/accounts/student_create.html'
    success_url = reverse_lazy('scheduling:admin_dashboard')

    def test_func(self):
        return self.request.user.role == 'admin'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = 'student'
        user.is_approved = True  # Admins create approved students
        user.save()
        messages.success(self.request, f"Student {user.username} created successfully!")
        return super().form_valid(form)

class MarkNotificationsReadView(LoginRequiredMixin, View):
    def get(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return redirect(request.META.get('HTTP_REFERER', 'accounts:dashboard_redirect'))

class StudentCourseRegistrationView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    fields = ['registered_courses']
    template_name = 'student/course_registration.html'
    success_url = reverse_lazy('timetable:student_dashboard')

    def test_func(self):
        return self.request.user.role == 'student'

    def get_object(self):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit course selection to student's department and level
        from apps.academics.models import Course
        form.fields['registered_courses'].queryset = Course.objects.filter(
            department=self.request.user.department,
            level=self.request.user.level
        )
        return form

    def form_valid(self, form):
        messages.success(self.request, "Your course registration has been updated.")
        return super().form_valid(form)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')
