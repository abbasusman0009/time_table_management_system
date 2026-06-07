from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('generate/', views.GenerateTimetableView.as_view(), name='generate'),
    path('import-data/', views.ImportDataView.as_view(), name='import_data'),
    path('conflicts/', views.ConflictResolutionView.as_view(), name='conflicts_list'),
]
