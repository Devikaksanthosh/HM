from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import LabWorker, Pharmacist, Prescription, PrescriptionMedicine
from dasapp.models import Medicine

# Lab Worker Signup Form
class LabWorkerUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class LabWorkerProfileForm(forms.ModelForm):
    class Meta:
        model = LabWorker
        fields = ['profile_pic']  # Add other fields specific to LabWorker

# Pharmacist Signup Form
class PharmacistUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class PharmacistProfileForm(forms.ModelForm):
    class Meta:
        model = Pharmacist
        fields = ['profile_pic']  # Add other fields specific to Pharmacist

# Login Forms
class LabWorkerLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class PharmacistLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

# Prescription Forms
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'appointment', 'additional_notes']

class PrescriptionMedicineForm(forms.ModelForm):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all())
    dosage = forms.CharField(max_length=100)
    duration = forms.CharField(max_length=100)

    class Meta:
        model = PrescriptionMedicine
        fields = ['medicine', 'dosage', 'duration']