from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Room, TimeSlot

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

# Room Views
class RoomListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Room
    template_name = 'admin/venues/room_list.html'
    context_object_name = 'rooms'

class RoomCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Room
    fields = ['name', 'capacity', 'room_type', 'is_available']
    template_name = 'admin/venues/room_form.html'
    success_url = reverse_lazy('venues:room_list')

    def form_valid(self, form):
        messages.success(self.request, "Room created successfully.")
        return super().form_valid(form)

class RoomUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Room
    fields = ['name', 'capacity', 'room_type', 'is_available']
    template_name = 'admin/venues/room_form.html'
    success_url = reverse_lazy('venues:room_list')

# TimeSlot Views
class TimeSlotListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'admin/venues/timeslot_list.html'
    context_object_name = 'timeslots'

class TimeSlotCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = TimeSlot
    fields = ['day', 'start_time', 'end_time', 'slot_index']
    template_name = 'admin/venues/timeslot_form.html'
    success_url = reverse_lazy('venues:timeslot_list')

    def form_valid(self, form):
        messages.success(self.request, "Time slot added successfully.")
        return super().form_valid(form)
