from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    
    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    
    # Lecturers
    path('lecturers/', views.LecturerListView.as_view(), name='lecturer_list'),
    path('lecturers/create/', views.LecturerCreateView.as_view(), name='lecturer_create'),
    path('lecturers/<int:pk>/', views.LecturerDetailView.as_view(), name='lecturer_detail'),
    path('preferences/', views.LecturerPreferencesView.as_view(), name='lecturer_preferences'),
]
