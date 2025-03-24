from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dasapp.models import CustomUser, LabWorker, PatientReg, Pharmacist, Test, PatientReport, Medicine
from django.contrib.auth.hashers import make_password
from dasapp.EmailBackEnd import EmailBackEnd
from dasapp.forms import LabWorkerUserForm, LabWorkerProfileForm, PharmacistUserForm, PharmacistProfileForm

def BASE(request):
    return render(request, 'base.html')

def LOGIN(request):
    return render(request, 'login.html')

def doLogout(request):
    logout(request)
    return redirect('login')


def doLogin(request):
    if request.method == 'POST':
        user = EmailBackEnd.authenticate(request,
                                         username=request.POST.get('email'),
                                         password=request.POST.get('password')
                                         )
        if user!=None:
            login(request,user)
            user_type = user.user_type
            if user_type == '1':
                 return redirect('admin_home')
            elif user_type == '2':
                 return redirect('doctor_home')
            elif user_type == '3':
                return redirect('userhome')
            
            
        else:
                messages.error(request,'Email or Password is not valid')
                return redirect('login')
    else:
            messages.error(request,'Email or Password is not valid')
            return redirect('login')

def register_labworker(request):
    if request.method == "POST":
        user_form = LabWorkerUserForm(request.POST)
        profile_form = LabWorkerProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = '3'  # Lab Worker
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Lab Worker registered successfully!")
            return redirect('lab_worker_login')
    else:
        user_form = LabWorkerUserForm()
        profile_form = LabWorkerProfileForm()
    return render(request, 'lab_worker/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
    

def register_pharmacist(request):
    if request.method == "POST":
        user_form = PharmacistUserForm(request.POST)
        profile_form = PharmacistProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = '4'  # Pharmacist
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "Pharmacist registered successfully!")
            return redirect('pharmacist_login')
    else:
        user_form = PharmacistUserForm()
        profile_form = PharmacistProfileForm()
    return render(request, 'pharmacist/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
    
def login_labworker(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid credentials for Lab Worker')
            return render(request, 'lab_worker/login.html')

        user = authenticate(request, username=user.username, password=password)
        if user is not None and user.user_type == '3':  # Check user_type for Lab Worker
            login(request, user)
            return redirect('lab_worker_dashboard')
        else:
            messages.error(request, 'Invalid credentials for Lab Worker')

    return render(request, 'lab_worker/login.html')

def login_pharmacist(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid credentials for Pharmacist')
            return render(request, 'pharmacist/login.html')

        user = authenticate(request, username=user.username, password=password)
        if user is not None and user.user_type == '4':  # Check user_type for Pharmacist
            login(request, user)
            return redirect('pharmacist_dashboard')
        else:
            messages.error(request, 'Invalid credentials for Pharmacist')

    return render(request, 'pharmacist/login.html')



@login_required
def PROFILE(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        
        try:
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()
            messages.success(request, "Profile updated successfully")
        except:
            messages.error(request, "Failed to update profile")
    return redirect('profile')

@login_required
def CHANGE_PASSWORD(request):
    if request.method == "POST":
        current = request.POST.get('cpwd')
        new_pas = request.POST.get('npwd')
        user = request.user
        if user.check_password(current):
            user.set_password(new_pas)
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Current password is incorrect!')
    return render(request, 'change-password.html')

# ---------- LAB WORKER FUNCTIONALITIES ----------

@login_required
def lab_worker_dashboard(request):
    tests = Test.objects.all()
    return render(request, 'lab_worker/dashboard.html', {'tests': tests})

@login_required
def create_test(request):
    if request.user.is_superuser or hasattr(request.user, 'labworker'):
        if request.method == "POST":
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            Test.objects.create(name=name, description=description, price=price)
            return redirect('manage_tests')
        return render(request, 'lab_worker/create_test.html')
    else:
        messages.error(request, "You are not authorized to add tests.")
        return redirect('lab_worker_dashboard')

@login_required
def create_patient_report(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')  # Ensure this is passed from the form
        test_id = request.POST.get('test_id')
        report_data = request.POST.get('report_data')

        try:
            patient = PatientReg.objects.get(id=patient_id)  
            test = Test.objects.get(id=test_id)

            report = PatientReport(
                lab_worker=request.user.labworker, 
                patient=patient,  
                test=test, 
                report_data=report_data
            )
            report.save()
            return redirect('lab_worker_dashboard')
        except PatientReg.DoesNotExist:
            messages.error(request, "Patient not found.")
        except Test.DoesNotExist:
            messages.error(request, "Test not found.")
    
    tests = Test.objects.all()
    return render(request, 'lab_worker/create_report.html', {'tests': tests})


@login_required
def manage_tests(request):
    if request.user.is_superuser or hasattr(request.user, 'labworker'):
        tests = Test.objects.all()
        return render(request, 'lab_worker/manage_tests.html', {'tests': tests})
    else:
        messages.error(request, "You are not authorized to manage tests.")
        return redirect('lab_worker_dashboard')


@login_required
def lab_test_requests(request):
    if not hasattr(request.user, 'labworker'):
        return redirect('lab_worker_dashboard')
    
    test_requests = PatientReport.objects.filter(status='requested')
    return render(request, 'lab_worker/test_requests.html', {
        'test_requests': test_requests
    })

@login_required
def accept_test_request(request, request_id):
    if not hasattr(request.user, 'labworker'):
        return redirect('lab_worker_dashboard')
    
    try:
        test_request = PatientReport.objects.get(id=request_id, status='requested')
        test_request.lab_worker = request.user.labworker
        test_request.status = 'in_progress'
        test_request.save()
        messages.success(request, "Test request accepted successfully!")
    except PatientReport.DoesNotExist:
        messages.error(request, "Invalid test request")
    
    return redirect('lab_test_requests')

@login_required
def complete_test_report(request, request_id):
    if not hasattr(request.user, 'labworker'):
        return redirect('lab_worker_dashboard')
    
    test_request = get_object_or_404(PatientReport, id=request_id, lab_worker=request.user.labworker)
    
    if request.method == 'POST':
        report_data = request.POST.get('report_data')
        test_request.report_data = report_data
        test_request.status = 'completed'
        test_request.save()
        messages.success(request, "Test report completed successfully!")
        return redirect('lab_worker_dashboard')
    
    return render(request, 'lab_worker/complete_report.html', {
        'test_request': test_request
    })

# ---------- PHARMACIST FUNCTIONALITIES ----------

@login_required
def pharmacist_dashboard(request):
    medicines = Medicine.objects.all()
    return render(request, 'pharmacist/dashboard.html', {'medicines': medicines})

@login_required
def manage_medicines(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        Medicine.objects.create(name=name, description=description, quantity=quantity, price=price)
        return redirect('pharmacist_dashboard')
    return render(request, 'pharmacist/manage_medicines.html')

@login_required
def search_medicines(request):
    query = request.GET.get('query', '')
    medicines = Medicine.objects.filter(name__icontains=query)
    return render(request, 'pharmacist/search_medicines.html', {'medicines': medicines, 'query': query})


@login_required
def send_test_results(request):
    if request.method == "POST":
        report_id = request.POST.get('report_id')
        result_data = request.POST.get('result_data')

        try:
            report = PatientReport.objects.get(id=report_id)
            report.report_data = result_data
            report.status = 'completed'  # Update status to completed
            report.save()
            messages.success(request, "Test results sent to patient successfully!")
        except PatientReport.DoesNotExist:
            messages.error(request, "Invalid report ID.")
        
        return redirect('lab_worker_dashboard')  # Redirect to the lab worker's dashboard

    reports = PatientReport.objects.filter(lab_worker=request.user.labworker, status='pending')  # Fetch pending reports
    return render(request, 'lab_worker/send_test_results.html', {'reports': reports})

@login_required
def search_medicine(request):
    query = request.GET.get('query', '')
    medicines = Medicine.objects.filter(name__icontains=query)
    return render(request, 'user/search_medicine.html', {'medicines': medicines, 'query': query})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dasapp.models import Prescription, PrescriptionMedicine, DoctorReg, PatientReg, Appointment, Medicine
from dasapp.forms import PrescriptionForm

@login_required(login_url='/')
def create_prescription(request, appointment_id=None):
    doctor = get_object_or_404(DoctorReg, admin=request.user)
    appointment = None
    patient = None


    # If appointment ID is provided, fetch the appointment & patient
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        patient = appointment.pat_id

    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST)
        if prescription_form.is_valid():
            prescription = prescription_form.save(commit=False)
            prescription.doctor = doctor
            prescription.patient = patient  # This will be None if no appointment is selected
            prescription.appointment = appointment  # This will also be None if no appointment
            prescription.save()

            # Handle multiple medicines
            for key, value in request.POST.items():
                if key.startswith('medicine_'):
                    medicine_id = value
                    dosage = request.POST.get(f'dosage_{key.split("_")[1]}')
                    duration = request.POST.get(f'duration_{key.split("_")[1]}')
                    medicine = Medicine.objects.get(id=medicine_id)
                    PrescriptionMedicine.objects.create(
                        prescription=prescription,
                        medicine=medicine,
                        dosage=dosage,
                        duration=duration
                    )

            messages.success(request, 'Prescription created successfully!')
            return redirect('doctor_home')
    else:
        prescription_form = PrescriptionForm()

    medicines = Medicine.objects.all()
    return render(request, 'doc/create_prescription.html', {
        'prescription_form': prescription_form,
        'medicines': medicines,
        'appointment': appointment
    })

@login_required(login_url='/')
def view_prescriptions(request):
    if hasattr(request.user, 'pharmacist'):
        prescriptions = Prescription.objects.all()
    else:
        prescriptions = Prescription.objects.filter(doctor__admin=request.user)

    return render(request, 'pharmacist/view_prescriptions.html', {'prescriptions': prescriptions})

@login_required(login_url='/')
def prescription_detail(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    prescription_medicines = PrescriptionMedicine.objects.filter(prescription=prescription)
    return render(request, 'pharmacist/prescription_detail.html', {
        'prescription': prescription,
        'prescription_medicines': prescription_medicines
    })