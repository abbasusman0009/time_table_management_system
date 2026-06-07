from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from apps.academics.models import Department

class StudentRegistrationForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=True,
        empty_label="Select Department"
    )
    phone = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'department', 'phone')

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
