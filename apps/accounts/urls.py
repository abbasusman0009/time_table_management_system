from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.StudentRegistrationView.as_view(), name='register'),
    path('approve-student/<int:pk>/', views.ApproveStudentView.as_view(), name='approve_student'),
    path('admin-student-create/', views.AdminStudentCreateView.as_view(), name='admin_student_create'),
    path('notifications/read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    path('student/courses/', views.StudentCourseRegistrationView.as_view(), name='student_course_registration'),
    path('dashboard-redirect/', views.dashboard_redirect, name='dashboard_redirect'),
]
