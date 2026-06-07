from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('student/', views.StudentTimetableView.as_view(), name='student_dashboard'),
    path('lecturer/', views.LecturerScheduleView.as_view(), name='lecturer_dashboard'),
    path('lecturer/export/pdf/', views.export_lecturer_pdf, name='export_lecturer_pdf'),
    path('lecturer/export/excel/', views.export_lecturer_excel, name='export_lecturer_excel'),
    path('admin/<int:pk>/edit/', views.AdminTimetableEditView.as_view(), name='admin_timetable_edit'),
    path('admin/history/', views.AdminTimetableHistoryView.as_view(), name='admin_timetable_history'),
    path('admin/feedback/', views.AdminFeedbackListView.as_view(), name='admin_feedback_list'),
    path('export/<int:pk>/pdf/', views.export_timetable_pdf, name='export_pdf'),
    path('export/<int:pk>/excel/', views.export_timetable_excel, name='export_excel'),
    path('explorer/', views.TimetableExplorerView.as_view(), name='explorer'),
    path('student/feedback/', views.SubmitFeedbackView.as_view(), name='submit_feedback'),
]
