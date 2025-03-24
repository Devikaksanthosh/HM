
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin



# Register your models here.
class UserModel(UserAdmin):
    list_display =['username','email','user_type']
admin.site.register(CustomUser,UserModel)
admin.site.register(Specialization)
admin.site.register(DoctorReg)
admin.site.register(Appointment)
admin.site.register(Page)
admin.site.register(AddPatient)
admin.site.register(PatientReg)
admin.site.register(MedicalHistory)
admin.site.register(LabWorker)
admin.site.register(Pharmacist)
admin.site.register(Test)
admin.site.register(PatientReport)
admin.site.register(Medicine)
