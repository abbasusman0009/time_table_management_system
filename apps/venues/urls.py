from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    # Rooms
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/create/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_edit'),
    
    # TimeSlots
    path('timeslots/', views.TimeSlotListView.as_view(), name='timeslot_list'),
    path('timeslots/create/', views.TimeSlotCreateView.as_view(), name='timeslot_create'),
]
