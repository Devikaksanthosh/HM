from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER ={
        (1,'admin'),
        (2,'doc'),
        ('3', 'lab_worker'),
        ('4', 'pharmacist'),
    }
    user_type = models.CharField(choices=USER,max_length=50,default=1)

    profile_pic = models.ImageField(upload_to='media/profile_pic')
    

class Specialization(models.Model):
    sname = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sname
   
    

class DoctorReg(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    mobilenumber = models.CharField(max_length=11)
    specialization_id = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    regdate_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.admin:
            return f"{self.admin.first_name} {self.admin.last_name} - {self.mobilenumber}"
        else:
            return f"User not associated - {self.mobilenumber}"

class PatientReg(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    mobilenumber = models.CharField(max_length=11,unique=True)
    gender = models.CharField(max_length=100)
    address = models.TextField()
    regdate_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.first_name}"

class Appointment(models.Model):
    appointmentnumber = models.IntegerField(default=0)
    spec_id = models.ForeignKey(Specialization, on_delete=models.CASCADE,default=0)
    pat_id = models.ForeignKey(PatientReg, on_delete=models.CASCADE,default=0)    
    date_of_appointment = models.CharField(max_length=250)
    time_of_appointment = models.CharField(max_length=250)
    doctor_id = models.ForeignKey(DoctorReg, on_delete=models.CASCADE)
    additional_msg = models.TextField(blank=True)
    remark = models.CharField(max_length=250,default=0)
    status = models.CharField(default=0,max_length=200)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment on {self.date_of_appointment} at {self.time_of_appointment}"
    

class Page(models.Model):
    pagetitle = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    aboutus = models.TextField()
    email = models.EmailField(max_length=200)
    mobilenumber = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pagetitle

class AddPatient(models.Model):
    doctor_id = models.ForeignKey(DoctorReg, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    mobilenumber = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=200)
    gender = models.CharField(max_length=100)
    address = models.TextField()
    age = models.IntegerField()
    
    medicalhistory = models.TextField()
    regdate_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MedicalHistory(models.Model):
    pat_id = models.ForeignKey(AddPatient, on_delete=models.CASCADE, related_name='medical_histories', default=0)
    bloodpressure = models.CharField(max_length=250)
    weight = models.CharField(max_length=250)
    bloodsugar = models.CharField(max_length=250)
    bodytemp = models.CharField(max_length=250)
    prescription = models.TextField()
    visitingdate_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

 
class LabWorker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Temporarily allow NULL
    profile_pic = models.ImageField(upload_to='media/lab_worker_pics', null=True, blank=True)


class Pharmacist(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='media/pharmacist_pics', null=True, blank=True)



class Test(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Track who added the test
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

class PatientReport(models.Model):
    lab_worker = models.ForeignKey(LabWorker, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientReg, on_delete=models.CASCADE, null=True, blank=True)  # Store patient as FK
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    report_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Report for {self.patient_name} - {self.test.name}"
    

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class PatientReport(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    lab_worker = models.ForeignKey(LabWorker, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(PatientReg, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    doctor_notes = models.TextField(blank=True, null=True)
    report_data = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test.name} for {self.patient.admin.first_name} (Status: {self.status})"
    

from django.db import models
from dasapp.models import DoctorReg, PatientReg, Appointment, Medicine

class Prescription(models.Model):
    doctor = models.ForeignKey(DoctorReg, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientReg, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicine, through='PrescriptionMedicine')
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.admin.first_name} by Dr. {self.doctor.admin.first_name}"

class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medicine.name} - {self.dosage} for {self.duration}"